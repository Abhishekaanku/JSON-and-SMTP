import os,datetime,glob,json
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import tkinter.filedialog
import tkinter
#Gets directory path
def get_dir():
    print('Select Folder')
    path=tkinter.filedialog.askdirectory()
    print(path)
    return path,len(path)

#Gets a list of all files
def get_files(path):
    path+='/*.txt'
    file_list=glob.glob(path)
    return file_list

#Sorts the file according to date of modification
def sort(file_list):
    file_dic={}
    for i in file_list:
        file_dic[os.path.getmtime(i)]=i
    sorted_time=list(sorted(file_dic.keys()))
    time_dif=(sorted_time[-1]-sorted_time[0])/60
    sorted_file=[]
    for i in sorted_time:
        sorted_file.append(file_dic[i])
    max_m_time=os.path.getmtime(sorted_file[-1])
    return sorted_file,max_m_time,time_dif

#Extract file name from s given path
def get_file_name(file,pathLength):
    i=len(file)-1
    date=str(datetime.datetime.fromtimestamp(os.path.getmtime(file)))
    date=date[:len(date)-3]
    file=file[pathLength:]
    file=file+'\t'+date
    return file

#Parsing and printing of logs
def parse(files,pathLength,max_m_time):
    print("\t\tFilename\t\tDate Modified\t\t\tMsg_Cnt")
    values=[]     #Stores the parsed jsons as dictionay object
    for i in files:
        with open(i) as filehandler:
            data=json.load(filehandler)
        values.append(data["msg_cnt"])
    sum1=0
    mini=0
    maxi=0
    file_name=[]
    for i in values:
        if mini>i:
            mini=i
        if maxi<i:
            maxi=i
        sum1=sum1+i
    for i in files:
        file_name.append(get_file_name(i,pathLength))
    i=0
    lth=len(values)
    while i<lth:
        if i==lth-1:
            break
        if values[i]>=1:
            k=i
            for j in range(i+1,lth):
                if values[j]>values[k]:
                    if j-i==1:
                        print("Inreasing sequence")
                        print(get_file_name(files[k],pathLength),'\t',values[k])
                    print(get_file_name(files[j],pathLength),'\t',values[j])
                    k=j
                    if k==lth-1:
                        i=lth
                else:
                    i=j
                    if k!=i:
                        print()
                    break
            k=i
            for j in range(i+1,lth):
                if values[j]<values[k] and values[j]>0:
                    if j-i==1:
                        print("Decreasing sequence")
                        print(get_file_name(files[k],pathLength),'\t',values[k])
                    print(get_file_name(files[j],pathLength),'\t',values[j])
                    k=j
                    if k==lth-1:
                        i=lth
                else:
                    if k!=i:
                        i=j
                        print()
                    break
            
        else:
            i=i+1
    average=sum1/(len(values)-1)
    print("Average value is",average)
    print("Maximum Deviation")
    left_div=mini-average
    right_div=maxi-average
    print(left_div,right_div)
    return values,file_name

def fmt(x, y):
    return 'file: {x:}\nmsg_cnt: {y:0.2f}'.format(x = x, y = y)

class DataCursor(object):
    # http://stackoverflow.com/a/4674445/190597
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist when it is selected."""
    def __init__(self, artists,file_name, x = [], y = [], tolerance = 5, offsets = (-5, 5),
                 formatter = fmt, display_all = False):
        """Create the data cursor and connect it to the relevant figure.
        "artists" is the matplotlib artist or sequence of artists that will be 
            selected. 
        "tolerance" is the radius (in points) that the mouse click must be
            within to select the artist.
        "offsets" is a tuple of (x,y) offsets in points from the selected
            point to the displayed annotation box
        "formatter" is a callback function which takes 2 numeric arguments and
            returns a string
        "display_all" controls whether more than one annotation box will
            be shown if there are multiple axes.  Only one will be shown
            per-axis, regardless. 
        """
        self._points = np.column_stack((x,y))
        self.formatter = formatter
        self.offsets = offsets
        self.display_all = display_all
        self.artists = artists
        self.axes = tuple(set(art.axes for art in self.artists))
        self.figures = tuple(set(ax.figure for ax in self.axes))
        self.file_name=file_name
        self.annotations = {}
        for ax in self.axes:
            self.annotations[ax] = self.annotate(ax)
        for artist in self.artists:
            artist.set_picker(tolerance)
        for fig in self.figures:
            fig.canvas.mpl_connect('pick_event', self)

    def annotate(self, ax):
        """Draws and hides the annotation box for the given axis "ax"."""
        annotation = ax.annotate(self.formatter, xy = (0, 0), ha = 'right',
                xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                )
        annotation.set_visible(False)
        return annotation

    def snap(self, x, y):
        """Return the value in self._points closest to (x, y).
        """
        idx = np.nanargmin(((self._points - (x,y))**2).sum(axis = -1))
        return self._points[idx]
    def __call__(self, event):
        """Intended to be called through "mpl_connect"."""
        # Rather than trying to interpolate, just display the clicked coords
        # This will only be called if it's within "tolerance", anyway.
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        annotation = self.annotations[event.artist.axes]
        if x is not None:
            if not self.display_all:
                # Hide any other annotation boxes...
                for ann in self.annotations.values():
                    ann.set_visible(False)
            # Update the annotation in the current axis..
            x, y = self.snap(x, y)
            annotation.xy = x, y
            annotation.set_text(self.formatter(self.file_name[x],y))
            annotation.set_visible(True)
            event.canvas.draw()

def p2(event):
    root=tkinter.Tk()
    root.title('Credentials')
    root.geometry('440x180')
    root.resizable(0,0)
    app=tkinter.Frame(root)
    app.grid(row=0,column=0,sticky=tkinter.W)
    tkinter.Label(app,text='Enter your email address').grid(row=0,column=0,columnspan=2,sticky=tkinter.W)
    app.ent1=tkinter.Entry(app,width=40)
    app.ent1.grid(row=0,column=2,sticky=tkinter.W)
    tkinter.Label(app,text='Enter password').grid(row=1,column=0,sticky=tkinter.W)
    app.ent2=tkinter.Entry(app,width=40)
    app.ent2.grid(row=1,column=2,sticky=tkinter.W)
    app.ent2.config(show='*')
    tkinter.Label(app,text="Enter reciever's email addresss").grid(row=2,column=0,columnspan=2,sticky=tkinter.W)
    app.ent3=tkinter.Entry(app,width=40)
    app.ent3.grid(row=2,column=2,sticky=tkinter.W)
    tkinter.Button(app,text='  Ok  ',command=lambda:send(root,app)).grid(row=3,column=0,sticky=tkinter.W)

def send(root,app):
    import smtplib
    import base64
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    sender = app.ent1.get()
    TO = app.ent3.get()
    pwd=app.ent2.get()
    msg = MIMEMultipart()
    msg["To"] = TO
    msg["From"] = sender
    msg["Subject"] = 'MSG_CNT PLOT'
    msgText = MIMEText('msg_cnt variation graph')  
    msg.attach(msgText) 
    fp = open('abcd.png', 'rb')                                                    
    img = MIMEImage(fp.read(),name='abcd.png')
    img.add_header('Content-ID', '<{}>'.format('abcd.png'))
    msg.attach(img)
    fp.close()
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com',587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(sender,pwd)
        smtpObj.sendmail(sender, TO, msg.as_string())
        smtpObj.close()
        tkinter.Label(app,text='Mail successfully sent!',foreground='green').grid(row=4,column=0,sticky=tkinter.W)
    except Exception:
        text='Failed to send mail!. Possible reason:\nConnection Issue\n Gmail authentication failed'
        tkinter.Label(app,text=text,foreground='red').grid(row=4,column=0,sticky=tkinter.W)
    tkinter.Button(app,text='Quit',command=root.destroy).grid(row=5,column=0,sticky=tkinter.W)
        
    
def main():                                                  
    (path,pathLength)=get_dir()
    f_name=path.split('/')[-1]
    files=get_files(path)
    files_sorted,max_m_time,time_dif=sort(files)
    msg_cnt,file_name=parse(files_sorted,pathLength,max_m_time)
    file_np=[]
    for i in range(len(files)):
        file_np.append(i+1)
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    grp=plt.plot(file_np,msg_cnt,lw=1)
    axprev = plt.axes([0.3, 0.054, 0.32, 0.05405])
    bprev = Button(axprev, 'Send Mail')
    bprev.on_clicked(p2)
    ax.set_xlabel("Maximum difference of file modification time is "+str(round(time_dif,2))+' minutes')
    ax.set_ylabel('Msg count values')
    fig.suptitle(f_name)
    fig.savefig('abcd.png')
    DataCursor(grp,file_name,file_np,msg_cnt)
    plt.show()
    

main()
input("Press Enter to continue")    
