import wx
import wx_widget
import viewer_canvas
import model_elem
import file_reader

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800,900))
        self.models = model_elem.Models()
        self.name_list = ['None']#, 'test_model', 'test2_model']#, 'All']
        self.initui()
        self.Show()

        '''
        # ============= test object =================
        test = model_elem.Model()
        test.model_name = 'test_model'
        test.motion_name = 'test_motion'
        test.max_frame = 160
        test.fps = 30
        test.start_frame = 0
        test.end_frame = test.max_frame
        self.models.model_list.append(test)

        test2 = model_elem.Model()
        test2.model_name = 'test2_model'
        test2.motion_name = 'test2_motion'
        test2.max_frame = 200
        test2.fps = 30
        test2.start_frame = 0
        test2.end_frame = test2.max_frame
        self.models.model_list.append(test2)
        # ============= test object =================
        '''
    def initui(self):
        self.panel = wx.Panel(self)
        verticalbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetBackgroundColour('#dcdcdc')

        #canvas 출력
        horizontalbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.canvas = viewer_canvas.Canvas(self.panel)
        self.canvas.SetMinSize((700, 700))

        horizontalbox1.Add(self.canvas, wx.ALIGN_TOP | wx.ALIGN_CENTER)
        verticalbox.Add(horizontalbox1, 1, wx.EXPAND | wx.ALIGN_TOP | wx.ALL, 10)

        #model 선택 항목, model 제거, model file 이름, motion file 이름
        #선택된 model은 윤곽선 lighlight
        horizontalbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.model_combobox = wx_widget.Model_Combo_Box(self.panel)
        self.del_button = wx_widget.Del_Button(self.panel)
        model_name_label = wx.StaticText(self.panel, label="model name: ")
        self.model_name = wx.StaticText(self.panel)
        motion_name_label = wx.StaticText(self.panel, label="motion name: ")
        self.motion_name = wx.StaticText(self.panel)

        horizontalbox2.Add(self.model_combobox, 10, wx.ALIGN_LEFT | wx.RIGHT, 10)
        horizontalbox2.Add(self.del_button, 0, flag = wx.RIGHT, border = 10)
        horizontalbox2.Add(model_name_label, flag = wx.Bottom)
        horizontalbox2.Add(self.model_name, flag=wx.Bottom | wx.Center)
        horizontalbox2.Add(motion_name_label, flag= wx.Bottom | wx.LEFT, border= 170)
        horizontalbox2.Add(self.motion_name, flag=wx.Bottom | wx.ALIGN_RIGHT)
        verticalbox.Add(horizontalbox2, 2, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 10)

        #slider 출력, check box - pin check: pin 설정 해 놓으면 해당 model은 재생 관련 control 같이 수행
        #pin check된 model도 highlighting
        horizontalbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.play_slider = wx_widget.Play_Slider(self.panel)
        self.pin_check = wx_widget.Pin_Check(self.panel)
        self.pin_check.SetValue(False)

        horizontalbox3.Add(self.play_slider, wx.EXPAND)
        horizontalbox3.Add(self.pin_check, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER)
        verticalbox.Add(horizontalbox3, 2, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        #재생 시작 frame, 재생 종료 frame 설정, frame 재생 영역 설정 적용(refresh), 모델 bvh로 내보내기
        horizontalbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.start_label = wx.StaticText(self.panel, label="start frame: ")
        self.start_frame = wx_widget.Start_Frame(self.panel)
        self.end_label = wx.StaticText(self.panel, label="end frame: ")
        self.end_frame = wx_widget.End_Frame(self.panel)
        self.refresh_button = wx_widget.Refresh_Button(self.panel)
        self.export_button = wx_widget.Export_Button(self.panel)

        horizontalbox4.Add(self.start_label, flag = wx.Bottom | wx.ALIGN_LEFT)
        horizontalbox4.Add(self.start_frame, flag=wx.LEFT |wx.Bottom, border=5)
        horizontalbox4.Add(self.end_label, flag=wx.LEFT | wx.Bottom, border=10)
        horizontalbox4.Add(self.end_frame, flag=wx.LEFT | wx.Bottom, border=5)
        horizontalbox4.Add(self.refresh_button, flag = wx.LEFT | wx.Bottom, border= 20)
        horizontalbox4.Add(self.export_button, flag=wx.LEFT | wx.Bottom, border=5)
        verticalbox.Add(horizontalbox4, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        verticalbox.Add((-1, 10))

        self.panel.SetSizer(verticalbox)

        #파일 드래그 입력
        self.file_reader = file_reader.File_Drop(self)
        self.SetDropTarget(self.file_reader)

def main():
    app = wx.App()
    MainWindow(None, title= 'motion_player')
    app.MainLoop()


if __name__ == '__main__':
    main()
