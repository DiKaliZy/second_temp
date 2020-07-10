import wx
import model_elem

class File_Drop(wx.FileDropTarget):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame

    def OnDropFiles(self, x, y, filenames):
        for file_root in reversed(filenames):
            temp = 0
            index = 0
            file_type = ''
            file_name = ''

            #파일명, 확장자 확인
            for char in reversed(file_root):
                #확장자
                if char == '.':
                    file_type = file_root[-index:]
                    temp = index
                #파일명
                if char == '/':
                    file_name = file_root[(-index):-(temp + 1)]
                    break
                index = index+1

            if file_type == 'bvh':
                new_model = self.bvh_file_read(file_name, file_root)
                #bvh file 확인
                #new_model.print_hierarchy(new_model.joint_root)
                #for joint in new_model.joint:
                #    print(joint.name)

            #elif file_type == 'asf':

            #elif file_type == 'amc':

            print('type: ', file_type)
            print('name: ', file_name)

        return True

#파일 읽었을 때 data 생성
    #bvh
    def bvh_file_read(self, file_name, file_root):
        #model object 정의 및 파일 정보 기록
        new_model = model_elem.Model()
        new_model.file_type = 'bvh'
        new_model.motion_name = file_name
        new_model.model_name = file_name

        #model object data 저장소 및 프로그램에 등록
        self.frame.models.model_list.append(new_model)
        self.frame.name_list.append(file_name)
        self.frame.model_combobox.Clear()
        self.frame.model_combobox.Set(self.frame.name_list)

        #file open and parsing
        file = open(file_root, 'r')
        lines = file.readlines()
        is_it_hierarchy = True       # bvh 파일이 hierarchy 인지 motion인지 확인

        new_joint = None
        old_joint = None

        for line in lines:
            line = line.strip()
            line = line.replace(":", "")
            line = line.split()

            if line[0] == "MOTION":
                is_it_hierarchy = False

            if is_it_hierarchy == True:
                #print(line[0])
                if line[0] == "JOINT":
                    new_joint = model_elem.Joint(line[1], new_model)
                    new_model.joint.append(new_joint)
                    new_model.joint_num += 1
                elif line[0] == "ROOT":
                    new_joint = model_elem.Joint(line[1], new_model)
                    new_joint.root = True
                    new_model.joint_root = new_joint
                    new_model.joint.append(new_joint)
                    new_model.joint_num += 1
                elif line[0] == "OFFSET":
                    old_joint.offset = list(map(float, line[1:4]))      #str array 형태를 float array로 변경
                elif line[0] == "CHANNELS":
                    channels = int(line[1])
                    old_joint.order = line[2:2 + channels]
                elif line[0] == "End":
                    new_joint = model_elem.Joint('End_' + old_joint.name, new_model)
                    new_joint.parent = old_joint
                    new_model.joint.append(new_joint)
                elif line[0] == "{":
                    if new_joint.root == False:
                        new_joint.parent = old_joint
                        old_joint.child.append(new_joint)
                        old_joint = new_joint
                    else:
                        old_joint = new_joint
                elif line[0] == "}":
                    old_joint = old_joint.parent
                elif line[0] == "HIERARCHY":
                    pass
                else:
                    msg = "Error opening bvh file\n {}".format(str("bvh 파일에 문제가 있습니다.\n(지원하지 않는 문자가 들어간 파일)"))
                    dlg = wx.MessageDialog(None, msg)
                    dlg.ShowModal()
                    self.frame.models.model_list.pop(-1)
                    return None

            elif is_it_hierarchy == False:
                if line[0] == "Frames":
                    new_model.max_frame = int(line[1]) - 1
                    new_model.end_frame = new_model.max_frame
                elif line[0] == "Frame":
                    new_model.fps = float(line[2]) * 1000
                elif line[0] != "MOTION":
                    motion_per_frame = list(map(float, line))
                    new_model.bvh_motion_injection(new_model.joint_root, motion_per_frame)
        return new_model