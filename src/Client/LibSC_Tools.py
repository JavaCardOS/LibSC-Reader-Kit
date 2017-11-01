
'''
Created on 2017-03-07

@author: javacardos@gmail.com
@organization: http://www.javacardos.com/
@copyright: JavaCardOS Technologies. All rights reserved.
'''
import wx
import LibSC

MYTE_WIDTH = 175
MYTE_MULHIGH = 140

g_serObj    = None

g_strPasswd = "ffffffffffff"
g_strPort   = "COM3"    #input
g_nSector   = 0

g_strDefComPort = "COM3"

g_bCloneCard    =False
g_strCloneCard  ="(clone)"

g_bHasCopyUid   =False
g_strCopyUid    =""
g_strUid        =""


class InputDlg(wx.Dialog):
    def __init__(
            self, strInfo,nSector=0,parent=None, ID=-1, title="Setting", size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):
        self.CreateDlg(strInfo,nSector,parent,ID,title,size,pos,style,useMetal)

    def CreateDlg(self, strInfo,nSector,parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
        #TODO:self.Bind(wx.EVT_CLOSE, self.OnClose,pre)

        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle(wx.DIALOG_EX_METAL)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Input the sector number to %s"%strInfo)
        label.SetHelpText("This is the help text for the label")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "sector:")
        label.SetHelpText("number of sector")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        text = wx.TextCtrl(self, -1,str(nSector), size=(80,-1))
        self.edtSector = text
        text.SetHelpText("Here's some help text for field #1")
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)


        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


class SettingDlg(wx.Dialog):
    def __init__(
            self, parent=None, ID=-1, title="Setting", size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):
        self.LoadSetting()
        self.CreateDlg(parent,ID,title,size,pos,style,useMetal)

    def CreateDlg(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        self.Bind(wx.EVT_CLOSE, self.OnClose,pre)
        # This extra style can be set after the UI object has been created.
        if 'wxMac' in wx.PlatformInfo and useMetal:
            self.SetExtraStyle(wx.DIALOG_EX_METAL)


        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "setup COM port and password")
        label.SetHelpText("This is the help text for the label")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Port:")
        label.SetHelpText("name of the COM port")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        comList=['COM3' ,'COM4' ,'COM5' ,'COM6' ,'COM7' ,
                 'COM8' ,'COM9' ,'COM10','COM11','COM12',
                 'COM13','COM14','COM15','COM16','COM17',
                 'COM18','COM19','COM20',]
        #text = wx.TextCtrl(self, -1, "COM", size=(80,-1))
        cbo = wx.ComboBox(self, -1, g_strDefComPort, (15, 30), wx.DefaultSize,
                    comList, wx.CB_DROPDOWN)
        self.cboPort = cbo
        cbo.SetHelpText("Here's some help text for field #1")
        box.Add(cbo, 1, wx.ALIGN_CENTRE|wx.ALL, 5)


        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Password:")
        label.SetHelpText("This is the help text for the label")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        text = wx.TextCtrl(self, -1, g_strPasswd, size=(80,-1))
        self.edtPasswd = text
        text.SetHelpText("Here's some help text for field #2")
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
    def OnClose(self,evt):
        #TODO:auto value
        print "saving setting"
        self.SaveSetting()
        self.Destroy()

    def LoadSetting(self):
        global g_strDefComPort,g_strPasswd
        print "loading setting"

        try:
            f = open("setting.inf")

            strTmp = f.readline().strip('\n')
            if len(strTmp)>=4:
                 g_strDefComPort = strTmp

            strTmp = f.readline().strip('\n')
            if len(strTmp)>=12:
                g_strPasswd = strTmp

            f.close()
        except:
            pass

    def SaveSetting(self):
        f = open("setting.inf","w")
        strTmp = self.cboPort.GetValue().strip('\n')
        f.write(strTmp+'\n')
        strTmp = self.edtPasswd.GetValue().strip('\n')
        f.write(strTmp+'\n')
        f.close()

class LibSC_Frame(wx.Frame):
    def __init__(self,parent, title,strUid,strCardType):
        wx.Frame.__init__(self, parent, -1, 'LibSC Tools',size=(360, 280))

        self.InitVars()

        #TODO:exit
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        pnlMain = wx.Panel(self, -1)

        lblUid = wx.StaticText(pnlMain, -1, "UID:")
        edtUid = wx.TextCtrl(pnlMain, -1, strUid,size=(MYTE_WIDTH, -1),
        style=wx.TE_READONLY)
        edtUid.SetInsertionPoint(0)

        if self.bConnect:
            strBtnText = "Disconnect"
        else:
            strBtnText = "Connect"

        btnConnect = wx.Button(pnlMain, -1, strBtnText)
        self.Bind(wx.EVT_BUTTON, self.OnClickConnect, btnConnect)


        lblType = wx.StaticText(pnlMain, -1, "Card Type:")
        edtType = wx.TextCtrl(pnlMain, -1, strCardType, size=(MYTE_WIDTH, -1),
        style=wx.TE_READONLY)

        btnRead = wx.Button(pnlMain, -1, "Read")
        self.Bind(wx.EVT_BUTTON, self.OnClickRead, btnRead)
        btnRead.Enable(self.bConnect)

        lblData = wx.StaticText(pnlMain, -1, "Data:")
        edtData = wx.TextCtrl(pnlMain, -1,
            "24 46 0C 85 EB 08 04 00\n"
            "62 63 64 65 66 67 68 69\n"
            "00 00 00 00 00 00 00 00\n"
            "00 00 00 00 00 00 00 00\n"
            "00 00 00 00 00 00 00 00\n"
            "00 00 00 00 00 00 00 00\n"
            "00 00 00 00 00 00 FF 07\n"
            "80 69 FF FF FF FF FF FF\n",
            size=(MYTE_WIDTH,MYTE_MULHIGH),
            style=wx.TE_MULTILINE|wx.TE_READONLY)
        btnWrite = wx.Button(pnlMain, -1, "Write")
        self.Bind(wx.EVT_BUTTON, self.OnClickWrite, btnWrite)
        btnWrite.Enable(self.bConnect)

        btnCloneUid = wx.Button(pnlMain, -1, "CopyUID")
        self.Bind(wx.EVT_BUTTON, self.OnClickCloneUid, btnCloneUid)
        btnCloneUid.Enable(self.bConnect)

        self.edtUid = edtUid
        self.edtType = edtType
        self.edtData = edtData

        self.btnConnect = btnConnect
        self.btnRead = btnRead
        self.btnWrite = btnWrite
        self.btnCloneUid = btnCloneUid
        #Data view init
        self.ReadSectorData()

        sizerLeft = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        sizerLeft.AddMany([lblUid, edtUid,
        lblType, edtType,
        lblData,edtData,
        ])

        sizerRight = wx.BoxSizer(orient=wx.VERTICAL)
        sizerRight.Add(btnConnect)
        sizerRight.Add(btnRead)
        sizerRight.Add(btnWrite)
        sizerRight.Add(btnCloneUid)


        sizerMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        sizerMain.Add(sizerLeft)
        sizerMain.Add(sizerRight)

        pnlMain.SetSizer(sizerMain)

        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menuItem = menu1.Append(-1, "&Setting...")
        menuBar.Append(menu1, "&File")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnSettingClick, menuItem)

    def InitVars(self):
        self.bConnect = True

    def OnClickConnect(self, event):
        if self.bConnect == False:
            dlg = SettingDlg()
            dlg.CenterOnScreen()
            if dlg.ShowModal() == wx.ID_OK:
                self.btnConnect.Enable(False)
                self.btnConnect.SetLabel("Disconnect")

                strUid,strCardType = com_connect()
                self.edtUid.SetValue(strUid)
                self.edtType.SetValue(strCardType)

                self.bConnect = True

                self.btnRead.Enable()
                self.btnWrite.Enable()
                self.btnCloneUid.Enable()
                self.btnConnect.Enable()

                self.ReadSectorData()
        else:
            global g_bCloneCard
            com_disconnect()

            self.edtUid.SetValue("")
            self.edtType.SetValue("")
            self.edtData.SetValue("")

            self.bConnect = False
            self.btnConnect.SetLabel("Connect")
            self.btnRead.Enable(False)
            self.btnWrite.Enable(False)
            self.btnCloneUid.Enable(False)
            g_bCloneCard = False

    def ReadSectorData(self):
        bin_mifare_key = LibSC.HexToBin(g_strPasswd)
        nBlkCount = 4
        nStart = g_nSector*nBlkCount
        strData=""

        if LibSC.MF_AuthA(nStart,bin_mifare_key):
            print "AuthA %d ok"%nStart
            for i in range(nBlkCount):
                nBlk = nStart+i
                data = LibSC.MF_Read(nBlk)
                strData+= LibSC.BinToHex(data[:8])
                strData+= "\r"
                strData+= LibSC.BinToHex(data[8:])
                strData+= "\r"
        else:
            print "AuthA %d failed"%nStart

        self.edtData.SetValue(strData)

    def OnClickRead(self, event):
        if ShowDlg_Input("READ",g_nSector) == wx.ID_OK:
            self.ReadSectorData()

    def OnClickWrite(self, event):
        if ShowDlg_Input("WRITE",g_nSector) == wx.ID_OK:
            wx.MessageBox("Not implement in this version")

    def OnClickCloneUid(self,event):
        global g_strCopyUid,g_bHasCopyUid
        if g_bHasCopyUid == False:
            self.btnCloneUid.SetLabel("WriteUID")
            g_strCopyUid = g_strUid
            g_bHasCopyUid = True
            wx.MessageBox("UID(%s) has been copyed,please put a MIFARE CLONE card on the reader"%g_strCopyUid)
            self.OnClickConnect(None)
        else:
            if not g_bCloneCard:
                wx.MessageBox("This is not a MIFARE CLONE card")
                self.OnClickConnect(None)
                return
            nRet = wx.MessageBox("Write UID(%s) to current card"%g_strCopyUid,style=wx.OK|wx.CANCEL)
            if nRet==wx.OK:
                print "write new uid to card"
                LibSC.MF_SetUid(g_strCopyUid)
                self.OnClickConnect(None)
                self.OnClickConnect(None)

    def OnSettingClick(self,event):
        ShowDlg_Setting()

    def OnClose(self,event):
        #self.Destroy()
        wx.Exit()

def ShowDlg_Setting():
    global g_strPasswd,g_strPort
    dlg = SettingDlg()
    dlg.CenterOnScreen()
    nRet = dlg.ShowModal()
    if nRet == wx.ID_OK:
        g_strPasswd = dlg.edtPasswd.GetValue()
        g_strPort = dlg.cboPort.GetValue()
        print "saving setting"
        dlg.SaveSetting()
    return nRet

def ShowDlg_Input(strInfo,nSector):
    global g_nSector
    dlg = InputDlg(strInfo,nSector)
    dlg.CenterOnScreen()
    nRet = dlg.ShowModal()
    if nRet == wx.ID_OK:
        g_nSector = int(dlg.edtSector.GetValue())
    return nRet

def com_connect():
    global g_serObj,g_bCloneCard,g_strUid
    g_serObj = LibSC.InitComm(g_strPort)

    g_bCloneCard = LibSC.MF_IsClone()
    atqa,sak,uid = LibSC.Connect()
    LibSC.DumpSession(atqa,sak,uid)
    g_strUid = strUid = LibSC.BinToHex(uid)
    cardType = LibSC.GetCardType(sak)
    strCardType= LibSC.GetCardTypeString(cardType)
    if(g_bCloneCard):
        strCardType+=g_strCloneCard
        print  "Is a clone card"
    return strUid,strCardType

def com_disconnect():
    LibSC.FinalComm(g_serObj)

def main():

    app = wx.App(False)

    if ShowDlg_Setting() == wx.ID_OK:

        strUid = "11223344"
        strCardType = "Unknow"

        strUid,strCardType = com_connect()

        frame = LibSC_Frame(None,'Small edior',strUid,strCardType)
        frame.Show()
        app.MainLoop()

if __name__ == '__main__':
    main()