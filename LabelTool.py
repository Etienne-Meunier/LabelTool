import os
from fnmatch import fnmatch
from tkinter import *
from tkinter import Tk
import ntpath
from tkinter.filedialog import askopenfilename,askdirectory

import cv2
import pandas as pd

KEYS = {'KEY_SELECT': ord('s'), 'KEY_QUIT': ord('q'), 'KEY_BACKWARD': ord('b'), 'KEY_VALIDATE': ord('v'),
        'KEY_DELETE': ord('d')}

FOLDER_VIDEOS = ''
FOLDER_LABELS = ''

class LabelTool:

    filename = ''

    def __init__(self):
        """
        Initialise ttrackers and video reader using opencv functions
        Set up basic variables for the tracker and reporting
        """
        Tk().withdraw()
        self.folder_labels = askdirectory(initialdir=FOLDER_LABELS,title='Labels Directory')
        self.folder_videos = askdirectory(initialdir=FOLDER_VIDEOS,title='Videos Directory')
        self.select_video()
        cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
        self.video = cv2.VideoCapture(self.filename)
        self.loop = False
        self.finished_annotation = False
        if self.filename != '' :
            ret = False
            while not ret:
                ret, self.frame = self.video.read()
            self.tracker = cv2.TrackerCSRT_create()
            self.initBB = None
            self.report = []
            self.frame_nb = 0
            self.box = None
            self.step_back = 20
            self.loop = True

    def reset_tracker(self):
        """
        Reset the tracker in order to set a new one after
        """
        self.initBB = None
        self.box = None
        self.tracker = cv2.TrackerCSRT_create()

    @staticmethod
    def create_label_report_name(path):
        """
        Convert the path to the video to a unique file name to store the report
        Args:
            path: path of the video

        Returns: name of the csv file

        """
        n = path.replace('/', '_._').replace('.mov', ".csv")
        return n

    @staticmethod
    def create_video_path_report_name(path):
        """
        Convert the csv name into a video path
        Args:
            path: path of the csv

        Returns: path of the video

        """
        n = path.replace('_._', '/').replace('.csv', ".mov")
        return n

    def command_key(self):
        """
        le utilisateur presse une touche et la commande est interprete
        :return : break the loop (bool)
        """
        key = None
        ret = True
        while key not in KEYS.values():
            key = cv2.waitKey()

        if key == KEYS['KEY_SELECT']:
            self.reset_tracker()
            self.initBB = cv2.selectROI('frame', self.frame, fromCenter=False, showCrosshair=True)
            self.tracker.init(self.frame, self.initBB)

        if key == KEYS['KEY_QUIT']:
            self.loop = False  # Stop the loop

        if key == KEYS['KEY_BACKWARD']:
            self.frame_nb = (self.frame_nb - 20) if self.frame_nb > self.step_back else 0
            self.report = [a for a in self.report if a[0] < self.frame_nb]
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_nb)
            self.reset_tracker()
            ret, self.frame = self.video.read()


        if key == KEYS['KEY_VALIDATE']:
            box = list(map(int, self.box)) if self.box is not None else None
            self.report.append((self.frame_nb, box))  # add line in report
            print((self.frame_nb, box))
            self.frame_nb += 1
            ret, self.frame = self.video.read()

        if key == KEYS['KEY_DELETE']:
            self.reset_tracker()

        if self.frame is None or not ret:
            self.loop = False
            self.finished_annotation = True

    def select_video(self):
        """
        Extract a list of videos to process by comparing the repository of videos and the repository of the reports in
        order to take only the videos that are not labelled yet
        """
        if isinstance(self.folder_labels,str) and isinstance(self.folder_videos,str) :
            # List of reports
            labels = list()
            for path, subdir, files in os.walk(self.folder_labels):
                for name in files:
                    if fnmatch(name, '*.csv'): labels.append(name)

            # List of videos
            videos = list()
            for path, subdir, files in os.walk(self.folder_videos):
                for name in files:
                    if fnmatch(name, '*.mov'):
                        path_vid = os.path.join(path, name)
                        if LabelTool.create_label_report_name(path_vid) not in labels: videos.append(path_vid)

            # List Box selection
            ch = Tk()
            scrollbar = Scrollbar(ch)
            scrollbar.pack(side=RIGHT, fill=Y)

            listbox = Listbox(ch, width=100, height=50, yscrollcommand=scrollbar.set)
            for v in videos: listbox.insert(END, v)
            listbox.pack(side=LEFT, fill=BOTH)

            button = Button(ch, text='print', command=lambda: ch.quit())
            button.pack()
            ch.mainloop()
            self.filename = listbox.get(ACTIVE)
            ch.destroy()

    def tracker_frame(self):
        """
        Run the tracker on the current frame and actualise box
        """
        # (H, W) = self.frame.shape[:2]
        success = False
        if self.initBB is not None:
            (success, self.box) = self.tracker.update(self.frame)
        LabelTool.display_frame(self.frame,self.frame_nb,self.box)

    @staticmethod
    def display_frame(frame,frame_nb,box):
        """
        Make a copy of frame and display it after putting the annotations

        Args:t
            frame : frame to display
            frame_nb ; number of the frame to display
            box : box of the annotation, None if no annotation on this image
        """
        disp_frame = frame.copy()
        if box is not None:
            box = list(map(float, box))
            (x, y, w, h) = [int(v) for v in box]  # extract coordinate
            cv2.rectangle(disp_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(disp_frame, str(frame_nb), (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2, [0, 0, 255])
        cv2.imshow('frame', disp_frame)

    def export_report(self):
        """
        Export report to csv file
        """
        df = pd.DataFrame(self.report,columns=['frame_nb','position'])
        df.to_csv(os.path.join(self.folder_labels, LabelTool.create_label_report_name(self.filename)))

    def process_frames(self):
        '''
        Call the tracker, display and wait command of the user for one frame
        '''
        while self.loop:
            self.tracker_frame()
            self.command_key()
        self.video.release()
        cv2.destroyAllWindows()
        if self.finished_annotation : self.export_report()

    @staticmethod
    def show_me_labels(csv_path = None):
        if csv_path is None :
            Tk().withdraw()
            csv_path=askopenfilename(initialdir=FOLDER_LABELS)
        csv_name = ntpath.basename(csv_path)
        df = pd.read_csv(csv_path,converters={'position' : lambda x : x.strip('[]').split(', ')})
        video_path = LabelTool.create_video_path_report_name(csv_name)
        video = cv2.VideoCapture(video_path)
        cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
        for frame_nb in range(0,df.shape[0]):
            r, frame = video.read()
            box = df['position'][frame_nb]
            LabelTool.display_frame(frame, frame_nb, box if len(box) == 4 else None)
            key = cv2.waitKey()
            if key == KEYS['KEY_QUIT']:
                break
        video.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    lt = LabelTool()
    lt.process_frames()
    #LabelTool.show_me_labels()