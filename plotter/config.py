ffmpeg_frame_cmd = 'ffmpeg -v 24 -i {video_path} -vf "select=gte(n\,{frame_index})" -vframes 1 {output_path}'


ffmpeg_video = ' '.join([
        'ffmpeg -v 24',  # only show warnings or higher
        '-i {video_path}',  # input
        '-vf "select=gte(n\,{left_frame_idx}),setpts=PTS-STARTPTS" -vframes {number_of_frames}',  # subset selection
        '-crf 28',  # quality
        '-c:v h264',  # encoder
        '-pix_fmt yuv420p',  # squash warning
        '{output_path}'  # output path
    ])