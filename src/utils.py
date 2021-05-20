import os, sys, copy, time, json, random, argparse, tabulate, datetime, requests
from inputimeout import inputimeout, TimeoutOccurred

WARNING_BEEP_DURATION = (2000, 500)

try:
    import winsound

except ImportError:
    import os

    if sys.platform == "darwin":

        def beep(freq, duration):
            # brew install SoX --> install SOund eXchange universal sound sample translator on mac
            os.system(
                f"play -n synth {duration/1000} sin {freq} >/dev/null 2>&1")
    else:

        def beep(freq, duration):
            # apt-get install beep  --> install beep package on linux distros before running
            os.system('beep -f %s -l %s' % (freq, duration))

else:
    def beep(freq, duration):
        winsound.Beep(freq, duration)



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def error(text):
    print(bcolors.FAIL + text + bcolors.ENDC)



def warn(text):
    print(bcolors.WARNING + text + bcolors.ENDC)



def success(text):
    print(bcolors.OKGREEN + text + bcolors.ENDC)



def slot(text):
    print(bcolors.OKCYAN + text + bcolors.ENDC)



def post_telegram(url, bot_api_key, channel, message):
    print(f"\nPosting on Telegram...")
    request_url = url.format(bot_api_key, channel, message)
    resp = requests.get(request_url)

    if resp.status_code == 401:
        error('TELEGRAM === UNAUTHORIZED !! Access denied by server, check bot token.\n')
        pass

    elif resp.status_code == 403:
        error(f'TELEGRAM === FORBIDDEN !! You cant send message on the {channel}.\n')
        pass

    elif resp.status_code == 400:
        error(f'TELEGRAM === The provided message is either empty or too long.\n')
        pass

    elif resp.status_code == 200:
        success(f'TELEGRAM === Message posted on the {channel}.\n')

    else:
        pass



def prepareTelegramMessage(options):

    message = "\n\n"
    for center in options:
        message += f"\n*[{center['pincode']}]*\n"
        message += f"\n_{center['district_name']}_\n"

        for session in center['sessions']:
            age = session['min_age_limit']
            vaccine = session['vaccine']

            if 'vaccine_fees' in center:
                for vaccine_fee in center['vaccine_fees']:
                    if vaccine_fee['vaccine'] == session['vaccine']:
                        if vaccine_fee['fee']:
                            if int(vaccine_fee['fee']) > 0:
                                vaccine = f"{session['vaccine']} - {center['fee_type']}(Rs.{vaccine_fee['fee']})"
                            else:
                                vaccine = f"{session['vaccine']} - {center['fee_type']}"

            if (int(session['available_capacity_dose1']) > 0 or int(session['available_capacity_dose2']) > 0):
                if int(session['available_capacity_dose1']) > 0:
                    message += f"\n*[{vaccine} - Dose 1]    {session['date']} : {int(session['available_capacity_dose1'])} slots*"
                if int(session['available_capacity_dose2']) > 0:
                    message += f"\n*[{vaccine} - Dose 2]    {session['date']} : {int(session['available_capacity_dose2'])} slots*"
            elif int(session['available_capacity']) > 0:
                message += f"\n*[{vaccine} - Dose NA]    {session['date']} : {int(session['available_capacity'])} slots*"

        message += f"\n\nName: *{center['name']}*"
        message += f"\nPincode: *{center['pincode']}*"
        message += f"\nMin Age: *{age}*"
        message += f"\nAddress: {center['address']}\n"
        message += f"\n=================================\n"

    message += "\nhttps://selfregistration.cowin.gov.in/appointment\n"
    return message

def viable_options(resp, min_slots, min_age):
    options = []
    if len(resp['centers']) >= 0:
        for center in resp['centers']:
            sessions = []
            for session in center['sessions']:
                if (int(session['min_age_limit']) <= min_age) and (int(session['available_capacity']) >= min_slots):
                        sessions.append(session)

            if len(sessions) > 0:
                center["sessions"] = sessions
                options.append(center)

    return options



def check_calendar_by_district(url, request_header, district_name, district_ids, start_date, min_slots, min_age):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns list of vaccination centers & slots if available
    """
    try:
        print('===================================================================================')
        today = datetime.datetime.today()

        options = []
        for district in district_ids:
            formated_url = url.format(district, start_date)
            resp = requests.get(formated_url, headers=request_header)

            if resp.status_code == 401:
                error(formated_url)
                error('UNAUTHORIZED !! Access denied by server.\n')
                pass

            elif resp.status_code == 403:
                error(formated_url)
                error('FORBIDDEN !! Reduce refresh frequency may solve the issue.\n')
                pass

            elif resp.status_code == 200:
                resp = resp.json()
                if 'centers' in resp:
                    success(f"Centers available for {min_age}+ age in {district_name}({district}) from {start_date} as of {today.strftime('%d-%m-%Y %H:%M:%S')}: {len(resp['centers'])}")
                    options += viable_options(resp, min_slots, min_age)

            else:
                pass

        return options

    except Exception as e:
        error(str(e))



def prepare(url, request_header, district_name, district_ids, **kwargs):
    """
    This function
        1. Checks the vaccination calendar for available slots,
        2. Lists all viable options,
    """
    try:
        min_age = kwargs['min_age']
        min_slots = kwargs['min_slots']

        now = datetime.datetime.now()

        if now.hour >= 18:
            start_date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        else:
            start_date = datetime.datetime.today().strftime("%d-%m-%Y")

        options = check_calendar_by_district(url, request_header, district_name, district_ids, start_date, min_slots, min_age)

        return options

    except TimeoutOccurred:
        error("TimeoutOccurred")
        time.sleep(1)
        return



def display_table(dict_list):
    """
    This function
        1. Takes a list of dictionary
        2. Add an Index column, and
        3. Displays the data in tabular format
    """
    header = ['idx'] + list(dict_list[0].keys())
    rows = [[idx + 1] + list(x.values()) for idx, x in enumerate(dict_list)]
    print(tabulate.tabulate(rows, header, tablefmt='grid'))



def display_info_dict(details):
    print("\n")
    for key, value in details.items():
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                print(f"\t{key}:")
                display_table(value)
            else:
                print(f"\t{key}\t: {value}")
        elif isinstance(value, str) \
            and "hooks.slack.com" in str(value):
            print(f"\t{key}\t: ******************")
        else:
            print(f"\t{key}\t: {value}")
    print("\n")



def get_info(filename):
    print(f"Reading file {filename}")
    with open(filename, 'r') as f:
        data = json.load(f)

    return data
