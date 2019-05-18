# Label Tool 

Label tool is a basic and free labeling tool for videos, very intuitive to use it allows to label video with a bounding box around one object, it handles directly the video file and integrate a tracking tool that allow to do the labeling step faster.

![](demo.gif)

## Installation of the dependencies 

```
pip3 install -r requirements.txt
```

### Running LabelTool

```
python3 Labeling.py
```

You are then invited to select the **Folders** where you store the Labels and the Videos. The program will then compare the two and give you a list of videos that are not been labeled yet, you just have to select a video from the list to start. 

![](menu1.png)

You have then the labeling tool open with the frame number on the top left in red. 

Commands : 

| Key  | Command  | Comment                                         |
| ---- | -------- | ----------------------------------------------- |
| v    | Validate | Validate this labelisation and go to next frame |
| s    | Select   | Select the object on the image                  |
| d    | Delete   | Delete current selection                        |
| b    | Backward | Go back of 1 frame                              |
| q    | Quit     | Quit and save labelisation process              |

When you finished your Labels are saved in a csv file with a name base on the name of the video. 

Labels are stored in the form

`Frame_nb`, `position` with position format as `(x,y,w,h)`

#### Visualize Labels

```
python3 Visualize.py
```

You then have to select the CSV file containing the labels, the program will find back the video based on the original video folder and display the labeling along with the video. 


### To Do

- Support Multi-Objects labeling
- Add Labels-Name 
- Improve object tracking
- Nice to have : create a mode for segmentation
