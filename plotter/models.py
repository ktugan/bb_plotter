from django.db import models
from bb_binary import load_frame_container
import os
from . import media, utils


class Video(models.Model):
    video_name = models.TextField(primary_key=True)
    video_path = models.TextField()


class FrameContainer(models.Model):
    id = models.AutoField(primary_key=True)
    fc_id = models.DecimalField(max_digits=32, decimal_places=0, db_index=True)
    fc_path = models.TextField()
    video_name = models.TextField()

    def get_binary(self):
        return load_frame_container(self.fc_path)

    @property
    def video_path(self):
        return Video.objects.get(video_name=self.video_name).video_path


class Frame(models.Model):
    frame_id = models.DecimalField(max_digits=32, decimal_places=0, primary_key=True)
    fc = models.ForeignKey(FrameContainer)
    index = models.IntegerField()

    def __str__(self):
        return f'{self.frame_id} - {self.index}'

    def get_image_path(self, extract=None):
        """
        Gets the path to the image. Also enabled the option to extract the picture if not done yet.
        Options for extract are 'single' or 'all'.
        'single' extracts just that frame and returns the path.
        'all' extracts all frames of the containing framecontainer and returns the single frame path.
        """
        path = f'/tmp/{self.fc.video_name}/{self.index:04}.jpg'
        if os.path.exists(path):
            return path

        if extract is None:
            return None

        if extract == 'single':
            return media.extract_single_frame(self)

        if extract == 'all':
            image_folder = media.extract_frames(framecontainer=self.fc)
            return path

    @staticmethod
    def get_video_path(frame_ids):
        frames = [Frame.objects.get(frame_id=frame_id) for frame_id in frame_ids]
        if len(frame_ids) != len(frames):
            raise ValueError('Some or all frame_ids not found.')

        return media.extract_video(frames)

    @staticmethod
    @utils.filepath_cacher
    def plot_frame(frame_id, x, y, rot):
        """
        Plot a single frame with the given frame_id. `x`, `y` and `rot` have to be of the same length.

        Args:
            frame_id (int): single frame_id to be plotted
            x (List): list of x coordinates
            y (List): list of y coordinates
            rot (List): list of rotations

        Returns:

        """
        if not (len(x) == len(y) == len(rot)):
            raise ValueError('x, y and rot not of the same length.')

        frame = Frame.objects.get(frame_id=frame_id)
        return media.plot_frame(frame, x, y, rot)

    @staticmethod
    @utils.filepath_cacher
    def plot_video(data):
    def plot_video(data, fillgap=False):
        if fillgap:
            fids = [d['frame_id'] for d in data]
            i = 0
            while i < len(fids) - 1:
                fid1, fid2 = fids[i], fids[i+1]
                f1 = Frame.objects.get(frame_id=fid1)
                f2 = Frame.objects.get(frame_id=fid2)
                if f1.fc_id != f2.fc_id:
                    i += 1
                    continue
                if f2.index - f1.index == 1:
                    i += 1
                    continue
                fill_frame_ids = (
                    Frame.objects.filter(
                        fc_id=f1.fc_id,
                        index__gt=f1.index,
                        index__lt=f2.index
                    ).order_by('index').values_list('frame_id', flat=True)
                )
                for fill_frame_id in reversed(fill_frame_ids):  # reversed so we dont need to increment i
                    fill_frame_id = int(fill_frame_id)
                    fids.insert(i+1, fill_frame_id)
                    data.insert(i+1, {'frame_id': fill_frame_id})
                i += 1 + len(fill_frame_ids)

        return media.plot_video(data)
