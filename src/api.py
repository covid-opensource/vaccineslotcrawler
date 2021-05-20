#!/usr/bin/env python3
import os, sys, time, copy, argparse
from types import SimpleNamespace
from fake_useragent import UserAgent
from threading import Thread

from utils import get_info, display_info_dict, prepare, prepareTelegramMessage, post_telegram, error, warn, success, slot, beep, WARNING_BEEP_DURATION

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Pass district name.')
    args = parser.parse_args()

    input_filepath = os.path.join(os.getcwd(), "input.json")

    try:

        #Pick a random user agent
        user_agent = UserAgent()

        base_request_header = {
            'User-Agent': user_agent.random
        }

        if args.d:
            target_district_name = args.d
            request_header = copy.deepcopy(base_request_header)

            if os.path.exists(input_filepath):
                input_json = get_info(input_filepath)

                if "cowin" in input_json:
                    cowin_info = input_json["cowin"]

                    if "calender_api_url" in cowin_info:
                        url = cowin_info["calender_api_url"]
                    elif "calender_api_public_url" in cowin_info:
                        url = cowin_info["calender_api_public_url"]
                    else:
                        error(f"Missing server url in {input_filepath}.")
                        error("Exiting script...")
                        sys.exit(1)

                    if "telegram" in input_json:
                        telegram_info = input_json["telegram"]

                if "districts" in input_json:
                    if target_district_name in input_json["districts"]:
                        district_info = input_json["districts"][target_district_name]

                        if isinstance(district_info["min_age"], int):
                            min_age = int(district_info["min_age"])
                        else:
                            # Set default min_age as 18 years.
                            min_age = 18

                        if isinstance(district_info["min_slots"], int):
                            min_slots = int(district_info["min_slots"])
                        else:
                            # Set default min_slots as 5.
                            min_slots = 5


            else:
                error(f"Missing {input_filepath}")
                error("Exiting script...")
                sys.exit(1)

            info = SimpleNamespace(**district_info)

            options = prepare(url, request_header, target_district_name, district_info["district_ids"],
                                    min_age=min_age,
                                    min_slots=min_slots)


            if isinstance(options, list):
                if len(options) > 0:

                    telegram_message = prepareTelegramMessage(options)

                    print('===================================================================================')
                    # Print message in CYAN color.
                    slot(telegram_message)
                    print('===================================================================================')

                    logfile = f"log_{target_district_name}.txt"
                    log_folder = "logs"
                    logfilepath = os.path.join(os.getcwd(), log_folder, logfile)

                    prev_notif = ""
                    # print(logfilepath)
                    if os.path.exists(logfilepath):
                        f = open(logfilepath, "r")
                        prev_notif = f.read()

                    if prev_notif != telegram_message:

                        if "telegram_channel_id" in district_info:

                            if "bot_api_key" in telegram_info:
                                bot_api_key = telegram_info["bot_api_key"]

                            if "telegram_chat_url" in telegram_info:
                                telegram_chat_url = telegram_info["telegram_chat_url"]


                            status = post_telegram(telegram_chat_url,
                                            bot_api_key,
                                            district_info["telegram_channel_id"],
                                            telegram_message)

                            # beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])
                            thread = Thread(target=beep, args=(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1],))
                            thread.start()

                    else:
                        error("\n\nNo new slots, repeat message.\n\n")

                    # Writing results to a file
                    with open(logfilepath, "w+") as outfile:
                        outfile.write(telegram_message)

                else:
                    warn("\nbut NO SLOTS available.\n")

    except Exception as e:
        error(str(e))
        error('Exiting Script')

if __name__ == '__main__':
    main()
