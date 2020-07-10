#기능 구현 관련
#1. combo box widget으로 read된 motion file을 선택 (focused)
#2. focuse된 파일은 기본적으로 재생 관련 기능 제어 대상이 되며 추가적으로 삭제 및 재생 구간 설정, 슬라이더 조작 대상이 됨
#3. focused 이외에도 다중 파일의 재생 관련 기능을 일부 허용 (pinned)
#4. pinned 된 파일은 재생 관련 기능의 제어 대상 (재생 관련 조작의 대상이 됨)
#5. 재생 관련 조작은 space(재생, 일시정지), 방향키 좌/우(되감기, 앞으로 감기), 방향키 상/하(재생 배속 조절 - 임시), 미정(정지) 가 해당됨
#6. 구간 반복 설정 후 refresh 버튼을 눌러 구간 반복 지정하도록 함
#7. 구간 설정은 낮은 순번의 frame 부터 시작할 수도 있고 큰 순번의 frame 부터 시작해서 낮은 순번 frame에서 끝나도록 할 수도 있음
#(예 - 10번째 frame에서 시작 -> 100번째 frame에서 종료 /
# 100번째 frame에서 시작 -> 120번째 frame이 마지막 -> 0으로 돌아감 -> 10번째 프레임에서 종료)
#8. slider가 구간 반복 설정 시 현재 위치가 구간 밖이면 구간 시작 부분으로 가도록 설정, 구간 설정된 부분 밖으로 슬라이더 이동 불가하도록 설정
#9. combo box 옆 x 버튼은 해당 model 삭제 버튼

import wx

class Model_Combo_Box(wx.ComboBox):
    def __init__(self, panel):
        super().__init__(panel, style = wx.CB_READONLY, size=(200,30), choices=panel.GetParent().name_list,
                                     value=panel.GetParent().name_list[0])

        self.Bind(wx.EVT_COMBOBOX, self.Model_Select)
        self.frame = panel.GetParent()

    #combo box에서 모델 선택 시 해당 모델 element 선택 됨
    def Model_Select(self, event):
        selected_name = event.GetString()
        if selected_name == 'None':
            for model in self.frame.models.model_list:
                model.focused = False
                model.pinned = False

            #file name display 갱신
            self.frame.model_name.SetLabel('')
            self.frame.motion_name.SetLabel('')

            # slider 갱신
            self.frame.play_slider.SetMax(1)
            self.frame.play_slider.SetValue(0)

            # pin 갱신
            self.frame.pin_check.SetValue(False)

            # start, end frame 갱신
            self.frame.start_frame.SetValue('0')
            self.frame.end_frame.SetValue('1')

        #All option 사용 x
            '''
        elif selected_name == 'All':
            max_frame = 0
            max_start = 0
            for model in self.frame.models.model_list:
                model.focused = True
                if max_frame <= model.max_frame:
                    max_frame = model.max_frame
                    max_start = model.start_frame
                model.frames = model.start_frame
            self.frame.model_name.SetLabel('All model')
            self.frame.motion_name.SetLabel('')

            self.frame.play_slider.SetMax(max_frame)
            self.frame.play_slider.SetValue(max_start)
        '''

        else:
            #max_frame = 0
            #focused_max = 0
            for model in self.frame.models.model_list:
                #pin 된 것도 slider로 조작 하는 경우를 가정하고 만들었으나 계획 변경 됨
                '''
                if model.pinned == True:
                    if max_frame <= model.max_frame:
                        max_frame = model.max_frame
                '''
                if model.model_name != selected_name:
                    #select 되지 않은 model focused 비활성화
                    model.focused = False
                else:
                    #select 된 model focused 활성화
                    model.focused = True
                    focused_max = model.max_frame

                    #file name 갱신
                    self.frame.model_name.SetLabel(model.model_name)
                    self.frame.motion_name.SetLabel(model.motion_name)

                    #pin 갱신
                    self.frame.pin_check.SetValue(model.pinned)

                    #slider 갱신
                    self.frame.play_slider.SetMax(model.max_frame)
                    self.frame.play_slider.SetValue(model.frame)

                    #start, end frame 갱신
                    self.frame.start_frame.SetValue(str(model.start_frame))
                    self.frame.end_frame.SetValue(str(model.end_frame))

            # pin 된 것도 slider로 조작 하는 경우를 가정하고 만들었으나 계획 변경 됨
            '''
            if max_frame <= focused_max:
                max_frame = focused_max
            self.frame.play_slider.SetMax(max_frame)
            '''

class Del_Button(wx.Button):
    def __init__(self, panel):
        super().__init__(panel, -1, "X", size=(30,30))
        self.panel = panel
        self.frame = panel.GetParent()
        self.Bind(wx.EVT_BUTTON, self.Model_Delete)

    #현재 combobox value 값에 해당되는 model_list element 삭제
    def Model_Delete(self, event):
        targets = []
        for model in self.frame.models.model_list:
            if model.focused == True:
                #model list 조회 및 삭제
                targets.append(model)

            else:
                pass
        #전체 삭제
        for target in targets:
            self.frame.name_list.pop(self.frame.name_list.index(target.model_name))
            self.frame.models.model_list.pop(self.frame.models.model_list.index(target))
        # combo box 갱신
        self.frame.model_combobox.Clear()
        self.frame.model_combobox.Set(self.frame.name_list)
        self.frame.model_combobox.SetValue(self.frame.name_list[0])
        self.frame.model_name.SetLabel('')
        self.frame.motion_name.SetLabel('')
        # slider 갱신
        self.frame.play_slider.SetValue(0)
        self.frame.play_slider.SetMax(1)

class Play_Slider(wx.Slider):
    def __init__(self, panel):
        super().__init__(panel, value=0, maxValue=1, style=wx.SL_LABELS)
        self.frame = panel.GetParent()
        self.Bind(wx.EVT_SCROLL_CHANGED, self.scroll)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.scroll)

    def scroll(self, event):
        slider = event.GetEventObject()
        for model in self.frame.models.model_list:
            if model.focused == True:
                model.played = False
                model.frame = slider.GetValue()
                #구간 설정 시 시작 frame이 end frame보다 작거나 같은 경우 slider 범위 밖에 오는 것 방지
                if model.start_frame <= model.end_frame:
                    if model.frame < model.start_frame:
                        model.frame = model.start_frame
                    elif model.frame > model.end_frame:
                        model.frame = model.end_frame
                #구간 설정 시 시작 frame이 end frame보다 큰 경우 slider 범위 밖에 오는 것 방지
                elif model.start_frame > model.end_frame:
                    if model.frame < model.start_frame and model.frame > model.end_frame:
                        model.frame = model.start_frame
                self.frame.play_slider.SetValue(model.frame)
        self.frame.play_slider.Refresh()

class Pin_Check(wx.CheckBox):
    def __init__(self, panel):
        super().__init__(panel, label='pin')
        self.Bind(wx.EVT_CHECKBOX, self.pin_checked)
        self.frame = panel.GetParent()

    def pin_checked(self, event):
        pin = event.GetEventObject()
        pin_value = pin.GetValue()
        for model in self.frame.models.model_list:
            if model.focused == True:
                if pin_value == True:
                    model.pinned = True
                elif pin_value == False:
                    model.pinned = False

class Start_Frame(wx.TextCtrl):
    def __init__(self, panel):
        super().__init__(panel, size = (100, 30), style = wx.TE_RIGHT)
        self.frame = panel.GetParent()

class End_Frame(wx.TextCtrl):
    def __init__(self, panel):
        super().__init__(panel, size = (100, 30), style = wx.TE_RIGHT)
        self.frame = panel.GetParent()

class Refresh_Button(wx.Button):
    def __init__(self, panel):
        super().__init__(panel, label='Refresh', size = (70,30))
        self.frame = panel.GetParent()
        self.Bind(wx.EVT_BUTTON, self.refresh)

    def refresh(self, event):
        final_start_value = 0
        final_end_value = 0
        for model in self.frame.models.model_list:
            if model.focused == True:

                if int(self.frame.start_frame.GetValue()) <= model.max_frame:
                    model.start_frame = int(self.frame.start_frame.GetValue())
                else:
                    model.start_frame = 0
                if int(self.frame.end_frame.GetValue()) <= model.max_frame:
                    model.end_frame = int(self.frame.end_frame.GetValue())
                else:
                    model.end_frame = model.max_frame
                #시작 frame이 end frame 보다 작거나 같은 경우
                if model.start_frame <= model.end_frame:
                    if model.frame > model.end_frame or model.frame < model.start_frame:
                        model.frame = model.start_frame
                    #All 기능 구현 시 end frame이 가장 큰 frame 기준으로 UI 표현하려 했으나 All 기능 제거 됨
                    if final_end_value <= model.end_frame:
                        final_end_value = model.end_frame
                        final_start_value = model.start_frame
                #end frame이 시작 frame 보다 큰 경우
                else:
                    if model.frame > model.end_frame and model.frame < model.start_frame:
                        model.frame = model.start_frame
                    # All 기능 구현 시 end frame이 가장 큰 frame 기준으로 UI 표현하려 했으나 All 기능 제거 됨
                    if final_start_value <= model.start_frame:
                        final_start_value = model.start_frame
                        final_end_value= model.end_frame

        self.frame.play_slider.SetValue(final_start_value)
        self.frame.start_frame.SetValue(str(final_start_value))
        self.frame.end_frame.SetValue(str(final_end_value))

#focused motion model 반복 구간 부분 data bvh(예정) 형식으 export
class Export_Button(wx.Button):
    def __init__(self, panel):
        super().__init__(panel, label='Export', size=(70, 30))
        self.frame = panel.GetParent()