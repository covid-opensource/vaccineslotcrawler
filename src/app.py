import os, sys, time, argparse

from utils import get_info, error, warn, success, display_info_dict



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Pass district name, it should match with what you have added in input.json, it is case sensitive.')
    args = parser.parse_args()

    if args.d:
        district = args.d

        filefolder = os.getcwd()
        filepath = os.path.join(filefolder, "input.json")

        if os.path.exists(filepath):
            input_json = get_info(filepath)

            if "districts" in input_json:
                if district in input_json["districts"]:
                    district_info = input_json["districts"][district]
                    display_info_dict(district_info)

                    if isinstance(district_info["refresh_rate"], int):
                        refresh_rate = int(district_info["refresh_rate"])
                    else:
                        # Set default refresh_rate as 5 seconds
                        refresh_rate = 5
                else:
                    error(f"Missing {district} details in input.json")
                    error("Exiting script...")
                    sys.exit(1)

        else:
            print(f"Missing {filepath}")
            print("Exiting script...")
            sys.exit(1)

        cmd = f"python -u api.py -d {district}"

        while True:
            os.system(cmd)

            for i in range(refresh_rate, 0, -1):
                msg = f"Next update in {i} seconds.."
                print(msg, end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(1)

    else:
        error("District name argument is missing, Pass district name, it should match with what you have added in input.json, it is case sensitive.")
        error("Try -h or --help for more details.")
        error("Exiting script...")
        sys.exit(1)


if __name__ == '__main__':
    main()
