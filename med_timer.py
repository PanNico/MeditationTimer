#!/usr/bin/env python3

import json, re, time, os
import datetime

file = "session.json"

def validate_session(session: dict):
    if "music_directory" not in session:
        raise Exception("You haven't specified your music directory for this session!")

    if "music_player" not in session:
        raise Exception("You haven't specified your music player for this session!")

    def validate_duration(duration: str):
        return re.search("^\d+:\d+:\d+$", duration) is not None

    def validate_music_file(type_of_play: str, activity: dict):
        if type_of_play in activity:
                if len(activity[type_of_play]) == 0:
                    activity[type_of_play] = None
                    return

                music_file = f'{session["music_directory"]}/{activity[type_of_play]}'

                if not os.path.isfile(music_file):
                    raise Exception(f"couldn't find the file {music_file} set into {type_of_play}")
                else:
                    activity[type_of_play] = music_file

    for activity in session["session"]:
        if "activity" not in activity:
            raise Exception("found activity without a name")

        if "duration" not in activity:
            raise Exception(f'the activity\"{activity["activity"]}\" doesn\'t have a duration set')
        elif not validate_duration(activity["duration"]):
            raise Exception(f'the activity\"{activity["activity"]}\" doesn\'t have a valid duration set')

        if "pause_before_start" in activity and not validate_duration(activity["pause_before_start"]):
            raise Exception(f'the activity\"{activity["activity"]}\" doesn\'t have a valid pause_before_start set')
        elif "pause_before_start" not in activity:
            activity["pause_before_start"] = "0:0:0"
        
        validate_music_file("start_play", activity)
        validate_music_file("end_play", activity)



class Activity:
    def __init__(self, activity: dict):
            self.name = activity["activity"]
            duration = activity["duration"]
            self.duration = self.duration_in_seconds(duration)
            pause_before_start = activity["pause_before_start"]
            self.pause_before_start = self.duration_in_seconds(pause_before_start)
            self.start_play = None
            self.end_play = None

            if "start_play" in  activity:
                self.start_play = activity["start_play"]

            if "end_play" in  activity:
                self.end_play = activity["end_play"]


    def duration_in_seconds(self, duration: str):
        def hours_to_mins(hours: int):
            return hours*60

        def mins_to_secs(minutes: int):
            return minutes*60

        timing =dict() 
        timing.update({"hours" : re.search("^(\d+):\d+:\d+$", duration).group(1)})
        timing.update({"minutes" : re.search("^\d+:(\d+):\d+$", duration).group(1)})
        timing.update({"seconds" : re.search("^\d+:\d+:(\d+)$", duration).group(1)})

        tot_minutes = int(timing["minutes"])+hours_to_mins(int(timing["hours"]))
        return  int(timing["seconds"])+mins_to_secs(tot_minutes)

class Session:
    def __init__(self, session: dict):
        self.player = session["music_player"]
        self.activities = list()
        
        for activity in session["session"]:
            self.activities.append(Activity(activity))
    
    def _run_music(self, music_file: str):
        os.system(f'{self.player} {music_file}')

    def show_tot_durations(self):
        # atm it doesn't consider the duration of the audios
        tot_seconds = 0
        for activity in self.activities:
            tot_seconds = tot_seconds + activity.pause_before_start + activity.duration

        tot_seconds = datetime.timedelta(seconds=tot_seconds)
        return tot_seconds

    def run(self):
        for activity in self.activities:
            print(f'\nExecuting \"{activity.name}\"...')
            print(f'Doing Pause before start: {activity.pause_before_start} seconds ...')

            time.sleep(activity.pause_before_start)
            if activity.start_play is not None:
                self._run_music(activity.start_play)
            print(f"Let's start doing  \"{activity.name}\" for {activity.duration} seconds!")
            time.sleep(activity.duration)
            if activity.end_play is not None:
                self._run_music(activity.end_play)

if __name__ == "__main__":
    with open(file, "r") as f:
        session = json.load(f)

    validate_session(session)

    s = Session(session)
    print("\033c\033[3J", end='')
    print(f"Tot duration is {s.show_tot_durations()}")
    s.run()

