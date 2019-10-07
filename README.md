# Debug Video Server

__author__: D-Soft Team<br> 
__version__ : 1.0

## Contents

- [1. Download Source Code](#1-download-source-code)
- [2. Installation](#2-installation)
    - [2.1. Install back-end server side](#21-install-back-end-server-side)
    - [2.2. Install environment client](#22-install-environment-client)
- [3. User Control Interface](#3-user-control-interface)
    - [Start up control view](#start-up-control-view)
    - [Start debug video recording](#start-debug-video-recording)
    - [Stop debug video recording](#stop-debug-video-recording)
    - [View debug video](#view-debug-video)
    - [View reID calculation result](#view-reid-calculation-result)

## 1. Download Source Code

```bash
    # clone from gitlab
    $ git clone https://gitlab.com/ggml/aitl/debug-video-server
    $ cd debug-video-server
    
    # wget
    $ wget https://gitlab.com/ggml/aitl/debug-video-server/-/tags/debug-video-server-v1.0-rcX.zip
    $ unzip debug-video-server-v1.0-rcX.zip
    $ cd debug-video-server-v1.0-rcX
```

**- Note:** All scripts below must be run in folder `debug-video-server/`.


## 2. Installation 
### 2.1. Install Django server
#### Setup Environment for the first time

We recommend using python3.6 and a virtual environment created by virtualenv. For the first time installation, from `debug-video-server/` folder, you should run this scripts below to install virtual environment and python packages: 

```bash
$ virtualenv -p python3 venv
$ source activation.sh
(venv) $ pip install -r requirements_cpu.txt
```

**- Note:** This script below can help you to get out of virtual environment:

```bash
(venv) $ deactivate
$ 
```

**- Note:** If virtual environment is set up, In the next time you don't need to run this step again.

#### Start Django server

First, you need to access to virtual environment from `debug-video-server/` folder:

```bash
$ source activation.sh
(venv) $ 
```

For starting back-end server, from `debug-video-server/` folder, run this script below:

```bash
(venv) $ python app/manage.py runserver
```

### 2.2. Install VueJS server
#### Install Nodejs and NPM

```bash
$ sudo apt install nodejs.
$ node -v (v8.15.0^)
$ sudo apt install npm. (v6.4.1^)
$ sudo apt-get update.
```

##NOTE: update version for node

```bash
$ sudo apt-get install build-essential libssl-dev
$ curl -sL https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh -o install_nvm.sh
$ bash install_nvm.sh
$ source ~/.profile
$ nvm install v8.15.0
$ nvm use v8.15.0
```

#### Run and start VueJS server

- Coppy file "app/src/util/.env.example.js" to "app/src/util/.env.js"
+ config APP_URL
- For starting NodeJS server, from `debug-video-server/` folder,
run this script in terminal:

```bash
$ cd app/src
$ npm install
$ npm run serve
```

## 3. User Control Interface

### Start up control view

When start local server, the control GUI of Debug Video Server tool will be as following

![Start up screen](https://i.imgsafe.org/6e/6ee94de998.png)

Where:
- **(1):** Video recording duration setting. It defines time to open connection and start listenning for incoming stream data until close connection. 
    + Unit: second
    + Range: 10 ~ min of 3600 and max storage available
- **(2):** ReID result version.
    + v1.0: support for AWLBox V1.0 with vectorization vector size of 128 elements 
    + v1.5: support for AWLBox V1.5 with vectorization vector size of 256 elements
- **(3):** Start video recording. The button will be enable once duration setting value is valid
- **(4):** Stop recording while videos are being recorded
- **(5):** Toggle full screen view mode

### Start debug video recording 
After input valid duration setting and click start button, the video record processing initializing state is as following

![Initializing screen](https://i.imgsafe.org/6f/6f6284ccab.png)

Then video recording in progress state

![Recording screen](https://i.imgsafe.org/6f/6f6d6ce8b0.png)

### Stop debug video recording
During debug video recording process, user can press `STOP` button to stop it.

![Stop debug video recording confirmation](https://i.imgsafe.org/6f/6f77d2d4d2.png)

After pressing `STOP` button, a confirmation dialog will pop up to confirm the decision.
- Yes: Stop debug video recording immediately
- Cancel: Resume debug video recording

**- Note:** During confirmation dialog display, the video recording is still in processing, not paused
 
### View debug video
When Debug Video stream recording finish (recording duration is elapsed) or `STOP` button pressed, if record video data is existed, the Video Data display view is as following

![View debug video data](https://i.imgsafe.org/6f/6f92855b14.png)

Where:
- **(6):** Select camera to display debug video (only one selectable)
- **(7):** Load debug video of selected camera
- **(8):** Debug video display area
- **(9):** Debug video display control
    + Play/Pause: Toggle debug video playing/pausing
    + Next(>>)/Prev(<<): Navigate to next/previous frame at Pause state

### View reID calculation result
At Pause state, ReID calculation result of the paused frame is displayed on the right side

![ReID calculation data](https://i.imgsafe.org/70/704538b1c7.png)

Where:
- **(10):** List of TrackIDs that existing in the current pausing frame
- **(11):** List of top tracked objects arrange in order of whose vectorized vectore is most similar to the selected object in TrackID List. The detected objects are from data of selected camera of (14)
- **(12):** ReID ranking object list display navigation button (left, right)
- **(13):** Number of top most similar objects to display in ReID Object List
- **(14):** Select camera list (multiple choices) to get vectorize data for reID calculation results


