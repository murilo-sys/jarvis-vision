from pycaw.pycaw import AudioUtilities


class VolumeControler:
    def __init__(self):
        device = AudioUtilities.GetSpeakers()

        self.windows_volume = device.EndpointVolume
        self.volume_locked = True

    def change_by_the_distance(self, distance: int) -> int:

        min_dist = 25
        max_dist = 190

        # transform the distance to a percentage
        proportion = (distance - min_dist) / (max_dist - min_dist)
        percentage = int(proportion * 100)

        # secury point
        percentage = max(0, min(100, percentage))

        if self.volume_locked:
            return percentage

        self.windows_volume.SetMasterVolumeLevelScalar(percentage / 100.0, None)
        return percentage
