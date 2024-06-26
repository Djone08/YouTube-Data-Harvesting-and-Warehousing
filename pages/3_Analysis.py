import streamlit as st
import pandas as pd
from About import set_creds


if __name__ == '__main__':
    yt_api, yt_db = set_creds()

    questions = [
        '01.What are the names of all the videos and their corresponding channels?',
        '02.Which channels have the most number of videos, and how many videos do they have?',
        '03.What are the top 10 most viewed videos and their respective channels?',
        '04.How many comments were made on each video, and what are their corresponding video names?',
        '05.Which videos have the highest number of likes, and what are their corresponding channel names?',
        '06.What is the total number of likes and dislikes for each video, '
        'and what are their corresponding video names?',
        '07.What is the total number of views for each channel, and what are their corresponding channel names?',
        '08.What are the names of all the channels that have published videos in the year 2022?',
        '09.What is the average duration of all videos in each channel, '
        'and what are their corresponding channel names?',
        '10.Which videos have the highest number of comments, and what are their corresponding channel names?']

    '# Analysis'

    q = st.selectbox('Questions', questions)

    if q == questions[0]:
        df = yt_db.fetch_data('''select channels.thumbnails as channelThumbnails, channels.title as channelTitle,
        videos.thumbnails as videoThumbnails, videos.title as videoTitle
        from videos inner join channels on videos.channelId = channels.id''')
        cc = {'channelThumbnails': st.column_config.ImageColumn(label='channelThumbnails'),
              'channelTitle': st.column_config.TextColumn(label='channelTitle'),
              'videoThumbnails': st.column_config.ImageColumn(label='videoThumbnails')}
    elif q == questions[1]:
        df = yt_db.fetch_data(f'''select * from channels
        where videoCount = (select max(videoCount) from channels)''')
        if not df.empty:
            col = st.columns([.2, .3, .5])
            col[1].write(f'''<p>
                    <img src="{df.thumbnails.iloc[0]}"
                    alt="thumbnails" title="{df.id.iloc[0]}" style="border-radius:50%" />
                    </p>
                    ''', unsafe_allow_html=True)
            col[2].write(f'## {df.title.iloc[0]}')
            col[2].write(f'Videos Count : **{df.videoCount.iloc[0]}**')
            # col[1].caption(df.description.iloc[0])
            channelId = df.id.iloc[0]
            df = yt_db.fetch_data(f'''select thumbnails, title, description from videos
            where channelId = {channelId!r}''')
        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails')}
    elif q == questions[2]:
        df = yt_db.fetch_data('''select channels.thumbnails as channelThumbnails,
        channels.title as channelTitle, videos.thumbnails as videoThumbnails,
        videos.title as videoTitle, videos.viewCount as videoViewCount
        from videos inner join channels on videos.channelId = channels.id
        order by videoViewCount desc limit 10''')
        cc = {'channelThumbnails': st.column_config.ImageColumn(label='channelThumbnails'),
              'videoThumbnails': st.column_config.ImageColumn(label='videoThumbnails')}
    elif q == questions[3]:
        df = yt_db.fetch_data('select thumbnails, title, commentCount from videos')
        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails')}
    elif q == questions[4]:
        df = yt_db.fetch_data('''select channels.thumbnails as channelThumbnails,
        channels.title as channelTitle, videos.thumbnails as videoThumbnails, videos.title as videoTile,
        videos.likeCount as videoLikeCount
        from videos inner join channels on videos.channelId = channels.id
        order by videoLikeCount desc''')
        cc = {'channelThumbnails': st.column_config.ImageColumn(label='channelThumbnails'),
              'videoThumbnails': st.column_config.ImageColumn(label='videoThumbnails')}
    elif q == questions[5]:
        df = yt_db.fetch_data('''select thumbnails, title,
        (likeCount+dislikeCount) as sumOfLikeAndDislike from videos''')
        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails')}
    elif q == questions[6]:
        df = yt_db.fetch_data('select thumbnails, title, viewCount from channels')
        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails')}
    elif q == questions[7]:
        if yt_db.db_type == 'mysql':
            df = yt_db.fetch_data('''select distinct channels.thumbnails, channels.title from videos
            inner join channels on channels.id = videos.channelId where year(videos.publishedAt)="2022"''')
        elif yt_db.db_type == 'sqlite':
            df = yt_db.fetch_data('''select distinct channels.thumbnails, channels.title from videos
            inner join channels on channels.id = videos.channelId
            where strftime("%Y", videos.publishedAt)="2022"''')
        else:
            df = pd.DataFrame()
        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails')}
    elif q == questions[8]:
        if yt_db.db_type == 'mysql':
            df = yt_db.fetch_data('''select channels.thumbnails as thumbnails, channels.title as title,
            sec_to_time(avg(time_to_sec(videos.duration))) as averageDurationPerVideo from videos
            inner join channels where channels.id = videos.channelId
            group by channels.id order by averageDurationPerVideo''')
        elif yt_db.db_type == 'sqlite':
            df = yt_db.fetch_data('''select channels.thumbnails as thumbnails, channels.title as title,
            time(cast(avg(unixepoch(videos.duration)) as int), "unixepoch") as averageDurationPerVideo from videos
            inner join channels where channels.id = videos.channelId 
            group by channels.id order by averageDurationPerVideo''')
        else:
            df = pd.DataFrame()

        cc = {'thumbnails': st.column_config.ImageColumn(label='thumbnails'),
              'averageDurationPerVideo': st.column_config.TimeColumn(label='averageDurationPerVideo')
              }
    elif q == questions[9]:
        df = yt_db.fetch_data('''select channels.thumbnails as channelThumbnails,
        channels.title as channelTitle, videos.thumbnails as videoThumbnails,
        videos.title as videoTitle, videos.commentCount as videoCommentCount
        from videos inner join channels on videos.channelId = channels.id
        order by videoCommentCount desc''')
        cc = {'channelThumbnails': st.column_config.ImageColumn(label='channelThumbnails'),
              'videoThumbnails': st.column_config.ImageColumn(label='videoThumbnails')}
    else:
        df = pd.DataFrame()
        cc = {}

    if df.empty:
        st.info(':blue[Add Channels to the list Using Channel Search]', icon='ℹ️')
    else:
        st.dataframe(df, column_config=cc, hide_index=True)
