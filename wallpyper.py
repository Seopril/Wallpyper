# Checks for proper python version

# Imports
import sys
import os
import ctypes
import urllib.request
import requests
import mimetypes
import platform
import math
import subprocess

import praw
import progressbar
import configparser
import prawconfig

# Checks system version
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    print("This script requires Python version 3.6 to run")
    sys.exit(1)

# Initializes progress_bar variable globally
progress_bar = None


def setConfigFilePath():
    # Sets the App Data location by OS
    if 'APPDATA' in os.environ:
        confighome = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    else:
        confighome = os.path.join(os.environ['HOME'], '.config')

    # Sets the App Data directory
    configDir = os.path.join(confighome, 'Wallpyper')

    # Creates the App Data Directory
    if not os.path.exists(configDir):
        os.mkdir(configDir)

    # Creates the config.ini file
    global configFilePath
    configFilePath = os.path.join(configDir, 'config.ini')


# Create config file
def createConfigFile():
    try:
        config = open(configFilePath, "w")
        config.close()
    except Exception:
        "Error creating file"


# Write config file
def writeConfig():
    config = configparser.ConfigParser()
    config.read(configFilePath)

    try:
        config['DEFAULT']['subreddit'] = 'wallpaper'
        config['DEFAULT']['image_path'] = configFilePath
        config['DEFAULT']['resolution'] = '1920x1080'
        config['DEFAULT']['aspect_ratio'] = '16:9'
        config['DEFAULT']['limit_resolution'] = 'True'
        config['DEFAULT']['limit_aspect_ratio'] = 'True'
        config['DEFAULT']['allow_larger_resolution'] = 'True'
        config['DEFAULT']['allow_nsfw'] = 'False'
        config['DEFAULT']['sort_by'] = 'hot'
        config['DEFAULT']['sort_limit'] = '10'
        config['DEFAULT']['history'] = 'False'
        with open(configFilePath, "a") as configfile:
            config.write(configfile)
    except Exception as e:
        print('Failed to write to config file: ' + str(e))
        print(configFilePath)
        print("Error writting to config file")
        print(str(configFilePath))


def setHistoryPath():
    # Sets the App Data location by OS
    if 'APPDATA' in os.environ:
        confighome = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    else:
        confighome = os.path.join(os.environ['HOME'], '.config')

    # Sets the history file location
    global historyPath
    historyPath = os.path.join(confighome, 'Wallpyper', 'history.txt')


def writeHistory(post):
    try:
        history = open(historyPath, 'a')
        history.write(getPermalink(post))
        history.write('\n')
    except IOError:
        "Unable to open/create history"


def checkHistory(post):
    try:
        history = open(historyPath, 'r')
        if getPermalink(post) in history.read():
            return True
        else:
            return False
    except IOError:
        "Unable to open the history"


# Get User Sub
def getSettings():
    config = configparser.RawConfigParser()
    try:
        config.read(configFilePath)
    except IOError:
        print("File does not exist")
    userSub = config['DEFAULT']['subreddit']
    imagePath = config['DEFAULT']['image_path']
    userResolution = config['DEFAULT']['resolution']
    userAspectRatio = config['DEFAULT']['aspect_ratio']
    limitResolution = config.getboolean('DEFAULT', 'limit_resolution')
    limitAspectRatio = config.getboolean('DEFAULT', 'limit_aspect_ratio')
    largerResolution = config['DEFAULT']['allow_larger_resolution']
    allowNSFW = config.getboolean('DEFAULT', 'allow_nsfw')
    sortBy = config['DEFAULT']['sort_by']
    sortLimit = config['DEFAULT']['sort_limit']
    history = config.getboolean('DEFAULT', 'history')

    return \
        userSub, \
        imagePath, \
        userResolution, \
        userAspectRatio, \
        limitResolution, \
        limitAspectRatio, \
        largerResolution, \
        allowNSFW, \
        sortBy, \
        sortLimit, \
        history


# Get Post
def getPosts(userSub, sortBy, sortLimit):
    reddit = praw.Reddit(client_id=os.getenv('WALLPYPER_CLIENT_ID'),
                         client_secret=os.getenv('WALLPYPER_CLIENT_SECRET'),
                         user_agent='python/desktop:seopril.wallpyper:v0.0.01:')
    subreddit = reddit.subreddit(userSub)
    submission = subreddit.hot(limit=int(sortLimit))
    post = []
    for item in submission:
        post.append(item)
    return post


def checkNSFW(post):
    if post.over_18:
        return True
    elif not post.over_18:
        return False
    else:
        return None


def choosePost(posts,
               limitResolution,
               limitAspectRatio,
               userResolution,
               userHeight,
               userWidth,
               userAspectRatio,
               allowNSFW,
               largerResolution,
               history):
    validPosts = []

    if history:
        for post in posts:
            if checkHistory(post):
                pass
            else:
                validPosts.append(post)
    else:
        for post in posts:
            validPosts.append(post)
    # First check NSFW setting
    if not allowNSFW:
        for post in validPosts:
            if checkNSFW(post):
                validPosts.remove(post)
    else:
        print("NSFW posts are being allowed. \
            This can be changed in the user settings")
    # Second, check aspect ratio
    if limitAspectRatio:
        for post in validPosts:
            if getAspectRatio(post) == userAspectRatio:
                pass
            else:
                validPosts.remove(post)
    else:
        print("Not checking Aspect Ratio")

    # Third, check resolution
    if limitResolution:
        if largerResolution:
            for post in validPosts:
                height = getHeight(post)
                width = getWidth(post)
                if height < userHeight or width < userWidth:
                    validPosts.remove(post)
        else:
            for post in validPosts:
                resolution = getResolution(post)
                if resolution != userResolution:
                    validPosts.remove(post)

    # Make sure validPosts isn't empty
    if len(validPosts) == 0:
        print('Error: No valid posts were found!')
        sys.exit(2)
    else:
        return validPosts[0]


def getHeight(post):
    height = None
    try:
        source = (post.preview.get('images')[0].get('source'))
        height = source.get('height')
    except Exception:
        print('Unknown exception while parsing height')
    return height


def getWidth(post):
    width = None
    try:
        source = (post.preview.get('images')[0].get('source'))
        width = source.get('width')
    except Exception:
        print('Unknown exception while parsing width')
    return width


def getResolution(post):
    resolution = None
    width = getWidth(post)
    height = getHeight(post)
    resolution = f'{width}x{height}'
    return resolution


def getUserHeight(userResolution):
    userHeightStr = userResolution.split('x', 1)[0]
    userHeight = int(userHeightStr)
    return userHeight


def getUserWidth(userResolution):
    userWidthStr = userResolution.split('x', 1)[1]
    userWidth = int(userWidthStr)
    return userWidth


def getAspectRatio(post):
    aspectRatio = None
    try:
        source = (post.preview.get('images')[0].get('source'))
        width = source.get('width')
        height = source.get('height')
        gcd = math.gcd(width, height)
        x = int(width/gcd)
        y = int(height/gcd)
        aspectRatio = f'{x}:{y}'
    except Exception:
        pass
    return aspectRatio


def getPermalink(post):
    permalink = "http://reddit.com"+post.permalink
    return permalink


def getImageName(permalink):
    splitLink = permalink.split("/")
    name = splitLink[7]
    print(name)

    return name


def getTitle(post):
    title = post.title

    return title


def getImageURL(post):
    url = post.url

    return url


def getExtension(url):
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    if extension == '.jpe':
        extension = '.jpg'
    else:
        pass

    return extension


def display_progress(block_number, block_size, total_size):
    global progress_bar

    # Creates a progress_bar if it does not exist
    if not progress_bar:
        progress_bar = progressbar.ProgressBar(maxval=total_size)

    # Calculates the amount downloaded for the % complete
    downloaded = block_number * block_size

    # Starts and updates the progress bar
    if downloaded == 0:
        progress_bar.start()
    elif downloaded < total_size:
        progress_bar.update(downloaded)
    else:
        progress_bar.finish()


# Get Image
def getImage(url, image_path, image_name, extension):
    final_name = os.path.join(image_path, image_name+extension)
    try:
        urllib.request.urlretrieve(url, final_name, display_progress)
    except FileNotFoundError as e:
        print(f'FileNotFoundErorr, Error Message: {str(e)}')
    return final_name


def createDirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        pass


# Sets background
def setBackground(image, operatingSystem):
    if(operatingSystem == 'Windows'):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image, 0)
    elif(operatingSystem == 'Darwin'):
        # TODO: Implement Mac Compatibility
        print("Unable to test tihs application on Mac OS as of now")
        print("FIF")
    elif(operatingSystem == 'Linux'):
        # GDM
        try:
            subprocess.run(["/usr/bin/gsettings",
                            "set",
                            "org.gnome.desktop.background",
                            "picture-uri",
                            image],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           check=True,
                           text=True)
        except subprocess.CalledProcessError as e:
            print(f'Error: Exited with return code: {e.returncode}')
            print(f'Error: Exited with message: {e.stdout}')
            print("Unable to set background picture using gsettings")
        # KDE
        try:
            # TODO
            pass
        except Exception:
            # TODO
            pass
    else:
        print('Unable to determine OS type')
        print(operatingSystem)


def getOS():
    operatingSystem = platform.system()

    return operatingSystem


def main():
    # Sets the config file's location
    setConfigFilePath()

    # Checks if the config file exists. Creates it if it doesn't
    if not os.path.exists(configFilePath):
        createConfigFile()
        writeConfig()

    # Pull in and define user settings
    settings = getSettings()
    userSub = settings[0]
    imagePath = settings[1]
    userResolution = settings[2]
    userAspectRatio = settings[3]
    limitResolution = settings[4]
    limitAspectRatio = settings[5]
    largerResolution = settings[6]
    allowNSFW = settings[7]
    sortBy = settings[8]
    sortLimit = settings[9]
    history = settings[10]
    userHeight = getUserHeight(userResolution)
    userWidth = getUserWidth(userResolution)

    createDirectory(imagePath)
    if history:
        setHistoryPath()

    posts = getPosts(userSub, sortBy, sortLimit)
    post = choosePost(posts,
                      limitResolution,
                      limitAspectRatio,
                      userResolution,
                      userHeight,
                      userWidth,
                      userAspectRatio,
                      allowNSFW,
                      largerResolution,
                      history)

    permalink = getPermalink(post)
    url = getImageURL(post)
    name = getImageName(permalink)
    extension = getExtension(url)

    image = getImage(url, imagePath, name, extension)
    if history:
        writeHistory(post)

    setBackground(image, getOS())

if __name__ == "__main__":
    main()
