import socket
import wpf
from System.Windows import *
from System.Windows.Controls import *
import collections
import sys
import os
import time
from connect import *
patient = get_current("Patient")
machine_db=get_current("MachineDB")
roi_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
ch_count=0
for ch in roi_names:
   n=ch[0:5].upper()
   if n=="COUCH":
      ch_count+=1
if ch_count==0:
    ch_count=2

lebcont=0
for d in roi_names:
    if "CTRL." in d:
       lebcont += 1
       ctrleb=d
if lebcont != 1:
   raise Exception ("No Section or Strategy Selected. Please check!!!")
   os._exit()

stgleb=ctrleb.split('.')[1]
if stgleb=="IMRT" and ch_count==2:
   ac_list=["600CD","VARIAN 23CX","TrueBeamSN1403","TB1403FFF","UN-SN2240"]
   bm_list=["F1B4","F3B2","F1B4&2","BST4","BST7","AVG5","AVG7","AVG9"]
if stgleb=="IMRT" and ch_count==3:
   ac_list=["4082", "4082_FFF"]
   bm_list=["F1B4","F3B2","F1B4&2","BST4","BST7","AVG5","AVG7","AVG9"]
if stgleb=="VMAT" and ch_count==2:
   ac_list=["TrueBeamSN1403","TB1403FFF","UN-SN2240"]
   bm_list=["2 ARC","4 ARC","6 P-ARC","5ANG-10ARC","9ANG-9ARC"]
if stgleb=="VMAT" and ch_count==3:
   ac_list=["4082","4082_FFF"]
   bm_list=["2 ARC","4 ARC","6 P-ARC","5ANG-10ARC","9ANG-9ARC"]

class MyWindow(Window):

  def __init__(self):


     wpf.LoadComponent(self, 'RuiPlan.xaml')
     #self.Topmost=True
     self.WindowStartupLocation=WindowStartupLocation.CenterScreen

     #ac_list = ["4082","UN-SN2240","TrueBeamSN1403"]

     self.SelectAC.ItemsSource = ac_list
     self.SelectBM.ItemsSource = bm_list

  def ConfirmClicked(self, sender, event):

     ''' Gets the dose at the selected relative volume for the selected ROI '''
        
     ac_name = self.SelectAC.SelectedItem
     bm_name = self.SelectBM.SelectedItem
     comleb  = self.SelectBM.SelectedItem
     fdose   = self.fd.Text

     for ck in self.opck.Children:
         if ck.IsChecked:
            opleb="Y"
         else: 
            opleb="N"
     if ac_name == "" or bm_name== "":
     
         return

#     pswd=self.pwd.Password
#     if pswd.upper()==chr(65)+chr(67):
#        pass 
#     else:
#        raise Exception ("Wrong Password!!!")
#        os._exit()  

     text = "New plan with {0} beams have been built."

     self.Ptext.Text = text.format(bm_name)

     self.RelVolPanel.Visibility = Visibility.Visible
     with open("paratmp","wb") as fff:
          fff.write(ac_name + '\r\n' + bm_name+ '\r\n'+opleb+ '\r\n'+fdose+ '\r\n')


  def CloseClicked(self, sender, event):

     self.DialogResult = True

window = MyWindow()
window.ShowDialog()

hm=socket.gethostname()
liclist=[]
if os.path.exists('\\\SQL\\Share\\Public\\rayx\\ruiplanme.lic'):
    with open ('\\\SQL\\Share\\Public\\rayx\\ruiplanme.lic' ,'r') as lic:
         licn=lic.readlines()
         for user in licn:
             if len(user)>15:
                liclist.append(chr(int(user[0:3]))+chr(int(user[3:6]))+chr(int(user[6:9]))+chr(int(user[9:11])))
         if len(licn[0])==22:
             ex=licn[0][11:21]
             exdate=str(int(ex,8))[0:4]+'-'+str(int(ex,8))[4:6]+'-'+str(int(ex,8))[6:8]
             exstamp=time.mktime(time.strptime(exdate,"%Y-%m-%d"))
             if exstamp-int(time.time())>0:
                pass
             else:
                raise Exception ("No License or License Expired!!!")
                os._exit()
         else:
             raise Exception ("No License or License Expired!!!")
             os._exit()                           
         if hm in liclist:
             pass
         else:
             raise Exception ("No License or License Expired!!!")
             os._exit()  
else:
    raise Exception ("No License or License Expired!!!")
    os._exit()

with open ('paratmp' ,'r') as ptmp:
    lines=ptmp.readlines()
    machname=lines[0][0:-1]
    nob=lines[1][0:-1]
    optleb=lines[2][0:-1]
    fdose=int(lines[3][0:-1])
dos=[]
nfra=[]
pdos=[]
tarls=[]
dosls=[]
ctrleb=""
for m in roi_names:
   if "CTRL." in m:
       ctrlleb=m
   if patient.PatientModel.RegionsOfInterest[m].OrganData.OrganType == "Target":

       con=collections.Counter(m)
              
       if con['_']==2:
           pname=m
           nf=m.split('_')[1]
           dy=m.split('_')[2]
           tarls.append(m) 
           dos.append(int(dy))
           nfra.append(int(nf))
           dosls.append(int(dy))

       if con['_']==3:
           pname=m
           nf=m.split('_')[1]
           dy=m.split('_')[2]
           #tarls.append(m) 
           dos.append(int(dy))
           nfra.append(int(nf))
           #dosls.append(int(dy))


       if con['_']==1:   
           tarls.append(m)
           dostmp=m.split('_')[1]
           dosls.append(int(dostmp))

pdose=max(dos)
if (nfra[0]*fdose!=pdose):
   raise Exception ("Fraction Number And Total Dose Are Not Match")
   os._exit()

if len(ctrlleb)==0:
    raise Exception ("No Strategy Selected. Please check!!!")
    os._exit()  
else:
    if ctrlleb[-4:]=="IMRT":
       stg="SMLC"
    if ctrlleb[-4:]=="VMAT":
       stg="VMAT"
if machname in ['4082','4082_FFF','TrueBeamSN1403','TB1403FFF']:
   csblab='False'
else:
   csblab='True'
if machname in ["600CD","VARIAN 23CX"]:
    for ch in roi_names:
        if "Couch" in ch:
            patient.PatientModel.RegionsOfInterest[ch].DeleteRoi()

with CompositeAction('Add Treatment plan'):

  retval_0 = patient.AddNewPlan(PlanName="plan", PlannedBy="Achao", Comment="AutoPlan", ExaminationName="CT 1", AllowDuplicateNames=False)

  retval_0.SetDefaultDoseGrid(VoxelSize={ 'x': 0.3, 'y': 0.3, 'z': 0.3 })

  retval_1 = retval_0.AddNewBeamSet(Name="AutoPlan", ExaminationName="CT 1", MachineName=machname, NominalEnergy=None, Modality="Photons", TreatmentTechnique=stg, PatientPosition="HeadFirstSupine", NumberOfFractions=nfra[0], CreateSetupBeams=csblab, UseLocalizationPointAsSetupIsocenter=False, Comment="")


  retval_1.AddDosePrescriptionToRoi(RoiName=pname, DoseVolume=95, PrescriptionType="DoseAtVolume", DoseValue=pdose, RelativePrescriptionLevel=1, AutoScaleDose=False)

info=patient.QueryPlanInfo(Filter={'Name':'^{0}$'.format("plan")})
patient.LoadPlan(PlanInfo=info[0])

plan=patient.LoadPlan(PlanInfo=info[0])

#plan=get_current("plan")

structure_set=plan.GetStructureSet()

try:
    ptv_center=structure_set.RoiGeometries[pname].GetCenterOfRoi()
except:
    print '(Cannot access center of ROI{0}.Exiting script.'.format(pname)
    sys.exit()

iso={'x':ptv_center.x,'y':ptv_center.y,'z':ptv_center.z}

isox=round(ptv_center.x,2)
isoy=round(ptv_center.y,2)
isoz=round(ptv_center.z,2)

if isox>0:
   side='left'
else:
   side='right'
beam_set = get_current("BeamSet")


if (nob=='2 ARC'):

  with CompositeAction('Add beam (1, Beam Set: 2arc)'):

    retval_0 = beam_set.CreateArcBeam(ArcStopGantryAngle=181, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=179, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (2, Beam Set: 2arc)'):

    retval_1 = beam_set.CreateArcBeam(ArcStopGantryAngle=179, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=181, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_1.SetBolus(BolusName="")

if (nob=='4 ARC'):

  with CompositeAction('Add beam (1, Beam Set: 2arc)'):

    retval_0 = beam_set.CreateArcBeam(ArcStopGantryAngle=181, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=179, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (2, Beam Set: 2arc)'):

    retval_1 = beam_set.CreateArcBeam(ArcStopGantryAngle=179, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=181, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_1.SetBolus(BolusName="")

  with CompositeAction('Add beam (3, Beam Set: 2arc)'):

    retval_2 = beam_set.CreateArcBeam(ArcStopGantryAngle=181, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=179, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 2arc)'):

    retval_3 = beam_set.CreateArcBeam(ArcStopGantryAngle=179, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=181, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

if (nob=='6 P-ARC'):

  with CompositeAction('Add beam (1, Beam Set: 6arc)'):

    retval_0 = beam_set.CreateArcBeam(ArcStopGantryAngle=120, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=178, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 6arc)'):

    retval_1 = beam_set.CreateArcBeam(ArcStopGantryAngle=310, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=50, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_1.SetBolus(BolusName="")

  # CompositeAction ends


  with CompositeAction('Add beam (3, Beam Set: 6arc)'):

    retval_2 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=240, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

  # CompositeAction ends


  with CompositeAction('Add beam (4, Beam Set: 6arc)'):

    retval_3 = beam_set.CreateArcBeam(ArcStopGantryAngle=240, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=182, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")


  with CompositeAction('Add beam (5, Beam Set: 6arc)'):

    retval_4 = beam_set.CreateArcBeam(ArcStopGantryAngle=50, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=310, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

  with CompositeAction('Add beam (6, Beam Set: 6arc)'):

    retval_5 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=120, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")


if (nob=='5ANG-10ARC'):
  with CompositeAction('Add beam (1, Beam Set: 5ANG-10ARC)'):

    retval_0 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=0, CouchAngle=80, CollimatorAngle=10, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (2, Beam Set: 5ANG-10ARC)'):

    retval_1 = beam_set.CreateArcBeam(ArcStopGantryAngle=0, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=182, CouchAngle=80, CollimatorAngle=350, ApertureBlock=None)

    retval_1.SetBolus(BolusName="")

  with CompositeAction('Add beam (3, Beam Set: 5ANG-10ARC)'):

    retval_2 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=0, CouchAngle=40, CollimatorAngle=10, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 5ANG-10ARC)'):

    retval_3 = beam_set.CreateArcBeam(ArcStopGantryAngle=0, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=182, CouchAngle=40, CollimatorAngle=350, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

  with CompositeAction('Add beam (5, Beam Set: 5ANG-10ARC)'):

    retval_4 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=178, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (6, Beam Set: 5ANG-10ARC)'):

    retval_5 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=182, CouchAngle=0, CollimatorAngle=350, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

  with CompositeAction('Add beam (7, Beam Set: 5ANG-10ARC)'):

    retval_6 = beam_set.CreateArcBeam(ArcStopGantryAngle=0, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=178, CouchAngle=320, CollimatorAngle=10, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (8, Beam Set: 5ANG-10ARC)'):

    retval_7 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="8", Description="8", GantryAngle=0, CouchAngle=320, CollimatorAngle=350, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

  with CompositeAction('Add beam (9, Beam Set: 5ANG-10ARC)'):

    retval_8 = beam_set.CreateArcBeam(ArcStopGantryAngle=0, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="9", Description="9", GantryAngle=178, CouchAngle=280, CollimatorAngle=10, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (10, Beam Set: 5ANG-10ARC)'):

    retval_9 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="10", Description="10", GantryAngle=0, CouchAngle=280, CollimatorAngle=350, ApertureBlock=None)

    retval_9.SetBolus(BolusName="")



if (nob=='9ANG-9ARC'):
  with CompositeAction('Add beam (1, Beam Set: 9ANG-9ARC)'):

    retval_0 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=178, CouchAngle=0, CollimatorAngle=10, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (2, Beam Set: 9ANG-9ARC)'):

    retval_1 = beam_set.CreateArcBeam(ArcStopGantryAngle=20, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=182, CouchAngle=20, CollimatorAngle=350, ApertureBlock=None)

    retval_1.SetBolus(BolusName="")

  with CompositeAction('Add beam (3, Beam Set: 9ANG-9ARC)'):

    retval_2 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=20, CouchAngle=40, CollimatorAngle=10, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 9ANG-9ARC)'):

    retval_3 = beam_set.CreateArcBeam(ArcStopGantryAngle=20, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=182, CouchAngle=60, CollimatorAngle=350, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

  with CompositeAction('Add beam (5, Beam Set: 9ANG-9ARC)'):

    retval_4 = beam_set.CreateArcBeam(ArcStopGantryAngle=182, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=20, CouchAngle=80, CollimatorAngle=10, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

  # CompositeAction ends 
  with CompositeAction('Add beam (6, Beam Set: 9ANG-9ARC)'):

    retval_5 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=340, CouchAngle=280, CollimatorAngle=10, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 9ANG-9ARC)'):

    retval_6 = beam_set.CreateArcBeam(ArcStopGantryAngle=340, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=178, CouchAngle=300, CollimatorAngle=350, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

  with CompositeAction('Add beam (8, Beam Set: 9ANG-9ARC)'):

    retval_7 = beam_set.CreateArcBeam(ArcStopGantryAngle=178, ArcRotationDirection="Clockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="8", Description="8", GantryAngle=340, CouchAngle=320, CollimatorAngle=10, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

  # CompositeAction ends 

  with CompositeAction('Add beam (9, Beam Set: 9ANG-9ARCc)'):

    retval_8 = beam_set.CreateArcBeam(ArcStopGantryAngle=340, ArcRotationDirection="CounterClockwise", Energy=6, MachineCone=None, Isocenter={ 'x': isox, 'y':isoy, 'z': isoz }, Name="9", Description="9", GantryAngle=178, CouchAngle=340, CollimatorAngle=350, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

if (nob=='F1B4'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=165, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=135, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=225, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=195, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 


if (nob=='F1B4&2'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=165, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=135, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=40, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=320, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (6, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=225, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['6'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=195, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['7'].BeamMU = 0


if (nob=='F3B2'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=160, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=40, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=320, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=200, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

#ABCDEF

if (nob=='BST4' and side=='left'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=120, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=106, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=310, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=295, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 

if (nob=='BST7' and side=='left'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=120, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=106, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=40, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=320, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (6, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=310, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['6'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=295, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['7'].BeamMU = 0


if (nob=='BST4' and side=='right'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=62, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=48, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=251, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=237, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0


if (nob=='BST7' and side=='right'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=62, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=48, CouchAngle=0, CollimatorAngle=340, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=40, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=320, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (6, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=251, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['6'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=237, CouchAngle=0, CollimatorAngle=20, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['7'].BeamMU = 0


if (nob=='AVG5'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=140, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=60, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=300, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=230, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 


if (nob=='AVG7'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=150, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=100, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=50, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=310, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (6, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=260, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['6'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=210, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['7'].BeamMU = 0


if (nob=='AVG9'):
  with CompositeAction('Add beam (1, Beam Set: 1)'):

    retval_2 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="1", Description="1", GantryAngle=160, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_2.SetBolus(BolusName="")

    beam_set.Beams['1'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (2, Beam Set: 1)'):

    retval_3 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="2", Description="2", GantryAngle=120, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_3.SetBolus(BolusName="")

    beam_set.Beams['2'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (3, Beam Set: 1)'):

    retval_4 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="3", Description="3", GantryAngle=80, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_4.SetBolus(BolusName="")

    beam_set.Beams['3'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (4, Beam Set: 1)'):

    retval_5 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="4", Description="4", GantryAngle=40, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_5.SetBolus(BolusName="")

    beam_set.Beams['4'].BeamMU = 0

  # CompositeAction ends 
  with CompositeAction('Add beam (5, Beam Set: 1)'):

    retval_6 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="5", Description="5", GantryAngle=0, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_6.SetBolus(BolusName="")

    beam_set.Beams['5'].BeamMU = 0

  # CompositeAction ends 

  with CompositeAction('Add beam (6, Beam Set: 1)'):

    retval_7 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="6", Description="6", GantryAngle=320, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_7.SetBolus(BolusName="")

    beam_set.Beams['6'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (7, Beam Set: 1)'):

    retval_8 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="7", Description="7", GantryAngle=280, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_8.SetBolus(BolusName="")

    beam_set.Beams['7'].BeamMU = 0

  with CompositeAction('Add beam (8, Beam Set: 1)'):

    retval_9 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="8", Description="8", GantryAngle=240, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_9.SetBolus(BolusName="")

    beam_set.Beams['8'].BeamMU = 0

  # CompositeAction ends 


  with CompositeAction('Add beam (9, Beam Set: 1)'):

    retval_0 = beam_set.CreatePhotonBeam(Energy=6, BlockTray=None, Cone=None, MachineCone=None, Wedge=None, Isocenter={ 'x': isox, 'y': isoy, 'z': isoz }, Name="9", Description="9", GantryAngle=200, CouchAngle=0, CollimatorAngle=0, ApertureBlock=None)

    retval_0.SetBolus(BolusName="")

    beam_set.Beams['9'].BeamMU = 0

patient.Save()

info2=patient.QueryPlanInfo(Filter={'Name':'^{0}$'.format("plan")})
patient.LoadPlan(PlanInfo=info2[0])


#with open ('paratmp' ,'r') as ptmp:
#    lines=ptmp.readlines()
#    methname=lines[0:-1]
#with open ('xy.txt','w') as xy:
#    if (lines[1]=='2'):
#       xy.write("2")
#    else:
#       xy.write("6")

patient = get_current("Patient")
machine_db=get_current("MachineDB")
examination = get_current("Examination")


roi_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]

dos=[]
nfra=[]
pdos=[]
tarls=[]
dosls=[]
oarls=[]
oardosls=[]

for m in roi_names:

   if patient.PatientModel.RegionsOfInterest[m].OrganData.OrganType == "Target":
    
       con=collections.Counter(m)
               
       if con['_']==2:
           pname=m
           nf=m.split('_')[1]
           dy=m.split('_')[2]
           tarls.append(m) 
           dos.append(int(dy))
           nfra.append(int(nf))
           dosls.append(int(dy))
     
       if con['_']==3:
           pname=m
           nf=m.split('_')[1]
           dy=m.split('_')[2]
           #tarls.append(m) 
           dos.append(int(dy))
           nfra.append(int(nf))
           #dosls.append(int(dy))
      
       if con['_']==1:   
           tarls.append(m)
           dostmp=m.split('_')[1]
           dosls.append(int(dostmp))
     
    
   if patient.PatientModel.RegionsOfInterest[m].OrganData.OrganType == "OrganAtRisk":
       con2=collections.Counter(m)
             
       if con2['_']==1:
          oarls.append(m)
          oardos=m.split('_')[1]
          oardosls.append(int(oardos))  

pdose=max(dos)


info=patient.QueryPlanInfo(Filter={'Name':'^{0}$'.format("plan")})
patient.LoadPlan(PlanInfo=info[0])

plan=patient.LoadPlan(PlanInfo=info[0])
shdic=['SEA-HORSE','SEAHORSE','SEA HORSE']
hipdic=['HIPPO']
lendic=['LEN-R','LENS-R','LEN-L','LENS-L','LENL','LENR','L LENS','R LENS','LENS R','LENS L']
ondic=['ON-L','ON-R','OPTIC NERVE-R','OPTIC NERVE-L','ONL','ONR']
bsdic=['BRAINSTEM','BRAIN-STEM','BS']
corddic=['CORD','SPINALCORD','SPINALCORD (THORAX)']
lungdic=['LUNG-L','LUNGL','LUNG-R','LUNGR','LUNG (LEFT)','LUNG (RIGHT)','LUNG RIGHT','LUNG LEFT']
chiasmdic=['CHIASM','DSSS','OPTIC CHIASM','OPTIC CHISMA','CHISMA','OPTIC CHIASMA','OPTIC CHIASM','CHIASMA']
parotiddic=['PAROTID-R','PAROTID-L','PAROTID R','PAROTID L','PAROTIDGLAND (LEFT)','PAROTIDGLAND (RIGHT)']

femoraldic=['FEMORAL HEAD R','FEMORAL HEAD L','FEMORALHEAD (LEFT)','FEMORALHEAD (RIGHT)']
heartdic=['HEART']
liverdic=['LIVER']
kiddic=['KIDNEY-L','KIDNEY (LEFT)','KIDNEY-R','KIDNEY (RIGHT)','KIDNEY LEFT','KIDNEY RIGHT']
bladdic=['BLADDER']
rectumdic=['RECTUM']
redic=['1']


if ("B1" not in roi_names):
  with CompositeAction('ROI Algebra (B1)'):

    retval_1 = patient.PatientModel.CreateRoi(Name="B1", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)

    retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

    retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

  # CompositeAction ends 

if ("B1.5" not in roi_names):
  with CompositeAction('ROI Algebra (B1.5)'):

    retval_2 = patient.PatientModel.CreateRoi(Name="B1.5", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)

    retval_2.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

    retval_2.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

  # CompositeAction ends 

if ("B2" not in roi_names):
  with CompositeAction('ROI Algebra (B2)'):

    retval_3 = patient.PatientModel.CreateRoi(Name="B2", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)

    retval_3.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 2, 'Inferior': 2, 'Anterior': 2, 'Posterior': 2, 'Right': 2, 'Left': 2 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

    retval_3.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

  # CompositeAction ends 

if "BODYCTRL.IMRT"  in roi_names or "BODYCTRL.VMAT"  in roi_names:
  if "DSSX" not in roi_names:
    with CompositeAction('ROI Algebra (DSSX)'):
    
      retval_4 = patient.PatientModel.CreateRoi(Name="DSSX", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
    
      retval_4.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["B2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 5, 'Posterior': 5, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    
      retval_4.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


po=plan.PlanOptimizations[0]
opt_param = po.OptimizationParameters
opt_param.Algorithm.MaxNumberOfIterations=60
opt_param.DoseCalculation.IterationsInPreparationsPhase = 20
opt_param.DoseCalculation.ComputeFinalDose=True
opt_param.DoseCalculation.ComputeIntermediateDose=False

if ctrlleb[-4:]=="VMAT":
  opt_param.SegmentConversion.ArcConversionProperties.UseMaxLeafTravelDistancePerDegree=True
  opt_param.SegmentConversion.ArcConversionProperties.MaxLeafTravelDistancePerDegree=0.4

  for bs in opt_param.TreatmentSetupSettings[0].BeamSettings:
      bs.ArcConversionPropertiesPerBeam.MaxArcDeliveryTime=5.0

if ctrlleb[-4:]=="IMRT":
  opt_param.SegmentConversion.MaxNumberOfSegments=50
  opt_param.SegmentConversion.MinSegmentArea=4.0
  opt_param.SegmentConversion.MinSegmentMUPerFraction=4.0
  opt_param.SegmentConversion.MinNumberOfOpenLeafPairs=2
  opt_param.SegmentConversion.MinLeafEndSeparation=0.0
  for bs in opt_param.TreatmentSetupSettings[0].BeamSettings:
      bs.AllowBeamSplit=False


lenls=[]
onls=[]
bsls=[]
chiasmls=[]
lungls=[]
parotidls=[]
cordls=[]
kidls=[]
femoralls=[]
heartls=[]
liverls=[]
bladls=[]
rectumls=[]
shls=[]
hipls=[]
rels=[]
chiasmls=[]
#roi_names = [r.Name for r in patient.PatientModel.RegionsOfInterest]

#if patient.PatientModel.RegionsOfInterest[m].OrganData.OrganType == "OrganAtRisk":

for i in roi_names:
   
   if patient.PatientModel.RegionsOfInterest[i].OrganData.OrganType == "OrganAtRisk":
     conx=collections.Counter(i)
     if conx['_']==0:

       if i.upper() in lendic:
            lenls.append(i)

       if i.upper() in ondic:
            onls.append(i)     

       if i.upper() in parotiddic:
            parotidls.append(i) 

       if i.upper() in bsdic:
            bsls.append(i)

       if i.upper() in lungdic:
            lungls.append(i)

       if i.upper() in corddic:
            cordls.append(i)

       if i.upper() in heartdic:
            heartls.append(i)

       if i.upper() in liverdic:
            liverls.append(i)

       if i.upper() in kiddic:
            kidls.append(i)

       if i.upper() in femoraldic:
            femoralls.append(i)   

       if i.upper() in shdic:
            shls.append(i)

       if i.upper() in hipdic:
            hipls.append(i)

       if i.upper() in bladdic:
            bladls.append(i)
 
       if i.upper() in rectumdic:
            rectumls.append(i)

       if i.upper() in redic:
            rels.append(i)

       if i.upper() in chiasmdic:
            chiasmls.append(i)
     else:
       if i.split('_')[0].upper() in lendic:
            lenls.append(i)

       if i.split('_')[0].upper() in ondic:
            onls.append(i)

       if i.split('_')[0].upper() in parotiddic:
            parotidls.append(i)

       if i.split('_')[0].upper() in bsdic:
            bsls.append(i)

       if i.split('_')[0].upper() in lungdic:
            lungls.append(i)

       if i.split('_')[0].upper() in corddic:
            cordls.append(i)

       if i.split('_')[0].upper() in heartdic:
            heartls.append(i)

       if i.split('_')[0].upper() in liverdic:
            liverls.append(i)

       if i.split('_')[0].upper() in kiddic:
            kidls.append(i)

       if i.split('_')[0].upper() in femoraldic:
            femoralls.append(i)

       if i.split('_')[0].upper() in shdic:
            shls.append(i)

       if i.split('_')[0].upper() in hipdic:
            hipls.append(i)

       if i.split('_')[0].upper() in bladdic:
            bladls.append(i)
 
       if i.split('_')[0].upper() in rectumdic:
            rectumls.append(i)

       if i.split('_')[0].upper() in redic:
            rels.append(i)

       if i.split('_')[0].upper() in chiasmdic:
            chiasmls.append(i)
cnt=0
     
 
for di in dosls:
   dscale=int(di*1.03)
   with CompositeAction('Add Optimization Function'):
      retval_1 = po.AddOptimizationFunction(FunctionType="MinDVH", RoiName=tarls[cnt])
      retval_1.DoseFunctionParameters.DoseLevel = dscale
      retval_1.DoseFunctionParameters.PercentVolume = 100
      retval_1.DoseFunctionParameters.Weight = 100
    
   with CompositeAction('Add Optimization Function'):
      retval_2 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=tarls[cnt])
      retval_2.DoseFunctionParameters.DoseLevel = dscale
      retval_2.DoseFunctionParameters.PercentVolume = 0
      retval_2.DoseFunctionParameters.Weight = 100
   cnt=cnt+1

if 'HEADCTRL.IMRT' in roi_names or 'HEADCTRL.VMAT' in roi_names:
   if len(lenls) !=0:   #['Lens-L','Lens-R_400']
       for li in lenls:
          conli=collections.Counter(li)
          if conli['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_5 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=li)
               retval_5.DoseFunctionParameters.DoseLevel = int(pdose*0.185)
               retval_5.DoseFunctionParameters.Weight = 20
          else:
              if int(str(li.split('_')[1])) != 0:
                 with CompositeAction('Add Optimization Function'):
                    retval_5 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=li)
                    retval_5.DoseFunctionParameters.DoseLevel = int(str(li.split('_')[1]))
                    retval_5.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_15 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=li)
                    retval_15.DoseFunctionParameters.DoseLevel = int(str(li.split('_')[1]))
                    retval_15.DoseFunctionParameters.EudParameterA = 150
                    retval_15.DoseFunctionParameters.Weight = 30

   if len(onls) !=0:
       for oi in onls:
          conoi=collections.Counter(oi)
          if conoi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_6 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=oi)
               retval_6.DoseFunctionParameters.DoseLevel = int(pdose*0.83)
               retval_6.DoseFunctionParameters.Weight = 20    
          else:
              if  int(str(oi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_6 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=oi)
                    retval_6.DoseFunctionParameters.DoseLevel = int(str(oi.split('_')[1]))
                    retval_6.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_16 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=oi)
                    retval_16.DoseFunctionParameters.DoseLevel = int(str(oi.split('_')[1]))
                    retval_16.DoseFunctionParameters.EudParameterA = 150
                    retval_16.DoseFunctionParameters.Weight = 30

   if len(cordls) !=0:
       for ci in cordls:
          if 'cm' not in roi_names:
            with CompositeAction('ROI Algebra (cm)'):
               retval_0 = patient.PatientModel.CreateRoi(Name="cm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
               retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [ci], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 })
               retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
          else:
            pass 
          conci=collections.Counter(ci)
          if conci['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_7 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
               retval_7.DoseFunctionParameters.DoseLevel = int(pdose*0.64)
               retval_7.DoseFunctionParameters.Weight = 20   
          else:
              if int(str(ci.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_7 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
                    retval_7.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_7.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_15 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ci)
                    retval_15.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_15.DoseFunctionParameters.EudParameterA = 150
                    retval_15.DoseFunctionParameters.Weight = 30

   if len(bsls) !=0:
       for bsi in bsls:
          conbsi=collections.Counter(bsi)
          if conbsi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=bsi)
               retval_8.DoseFunctionParameters.DoseLevel = int(pdose*0.83)
               retval_8.DoseFunctionParameters.Weight = 20    
          else:
              if int(str(bsi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=bsi)
                    retval_8.DoseFunctionParameters.DoseLevel = int(str(bsi.split('_')[1]))
                    retval_8.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_16 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=bsi)
                    retval_16.DoseFunctionParameters.DoseLevel = int(str(bsi.split('_')[1]))
                    retval_16.DoseFunctionParameters.EudParameterA = 150
                    retval_16.DoseFunctionParameters.Weight = 30

   if len(chiasmls) !=0:
       for chisi in chiasmls:
          conchisi=collections.Counter(chisi)
          if conchisi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=chisi)
               retval_8.DoseFunctionParameters.DoseLevel = int(pdose*0.83)
               retval_8.DoseFunctionParameters.Weight = 20    
          else:
              if int(str(chisi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=chisi)
                    retval_8.DoseFunctionParameters.DoseLevel = int(str(chisi.split('_')[1]))
                    retval_8.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_16 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=chisi)
                    retval_16.DoseFunctionParameters.DoseLevel = int(str(chisi.split('_')[1]))
                    retval_16.DoseFunctionParameters.EudParameterA = 150
                    retval_16.DoseFunctionParameters.Weight = 30
    
   if len(parotidls) !=0:
       for pi in parotidls:
          conpi=collections.Counter(pi)
          if conpi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_9 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=pi)
               retval_9.DoseFunctionParameters.DoseLevel = int(pdose*0.58)
               retval_9.DoseFunctionParameters.EudParameterA = 1
               retval_9.DoseFunctionParameters.Weight = 5
          else:
              if int(str(pi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_9 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=pi)
                    retval_9.DoseFunctionParameters.DoseLevel = int(str(pi.split('_')[1]))
                    retval_9.DoseFunctionParameters.EudParameterA = 1
                    retval_9.DoseFunctionParameters.Weight = 15

   if len(lungls) !=0:
       if len(lungls)==2:
          if "Lung-Z" not in roi_names:
            with CompositeAction('ROI Algebra (Lung-Z)'):  
                 retval_0 = patient.PatientModel.CreateRoi(Name="Lung-Z", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)     
                 retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [lungls[0], lungls[1]], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })  
                 retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
               # CompositeAction ends
       for lgi in lungls:
          conlgi=collections.Counter(lgi)
          if conlgi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_10 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_10.DoseFunctionParameters.DoseLevel = int(pdose*0.13)
               retval_10.DoseFunctionParameters.PercentVolume = 45
               retval_10.DoseFunctionParameters.Weight = 5

            with CompositeAction('Add Optimization Function'):
               retval_10 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_10.DoseFunctionParameters.DoseLevel = int(pdose*0.35)
               retval_10.DoseFunctionParameters.PercentVolume = 22
               retval_10.DoseFunctionParameters.Weight = 5
          else:
              if int(str(lgi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=lgi)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(lgi.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15


   if len(shls) !=0:
       for shi in shls:
          with CompositeAction('Add Optimization Function'):
             retval_11 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=shi)
             retval_11.DoseFunctionParameters.DoseLevel = int(pdose*0.45)
             retval_11.DoseFunctionParameters.Weight = 20

          with CompositeAction('Add Optimization Function'):
             retval_12 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=shi)
             retval_12.DoseFunctionParameters.DoseLevel = int(pdose*0.3)
             retval_12.DoseFunctionParameters.EudParameterA = 1
             retval_12.DoseFunctionParameters.Weight = 5

   if len(hipls) !=0:
       for hipi in hipls:
          with CompositeAction('Add Optimization Function'):
             retval_13 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=hipi)
             retval_13.DoseFunctionParameters.DoseLevel = int(pdose*0.55)
             retval_13.DoseFunctionParameters.Weight = 20

          with CompositeAction('Add Optimization Function'):
             retval_14 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=hipi)
             retval_14.DoseFunctionParameters.DoseLevel = int(pdose*0.45)
             retval_14.DoseFunctionParameters.EudParameterA = 1
             retval_14.DoseFunctionParameters.Weight = 5

if 'BODYCTRL.IMRT' in roi_names  or 'BODYCTRL.VMAT' in roi_names:
   if len(femoralls) !=0:
       for fi in femoralls:
          confi=collections.Counter(fi)
          if confi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_5 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=fi)
               retval_5.DoseFunctionParameters.DoseLevel = int(pdose*0.65)            
               retval_5.DoseFunctionParameters.PercentVolume = 50
               retval_5.DoseFunctionParameters.Weight = 5
          else:
              if int(str(fi.split('_')[1]))!=0:
                  with CompositeAction('Add Optimization Function'):
                     retval_5 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=fi)
                     retval_5.DoseFunctionParameters.DoseLevel = int(str(fi.split('_')[1]))
                     retval_10.DoseFunctionParameters.EudParameterA = 1
                     retval_10.DoseFunctionParameters.Weight = 15
       
   if len(bladls) !=0:
       for bi in bladls:
          conbi=collections.Counter(bi)
          if conbi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_6 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=bi)
               retval_6.DoseFunctionParameters.DoseLevel = int(pdose*0.91)
               retval_6.DoseFunctionParameters.PercentVolume = 50    
               retval_6.DoseFunctionParameters.Weight = 5
          else:
              if int(str(bi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=bi)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(bi.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15
    
   if len(rectumls) !=0:
       for ri in rectumls:
          conri=collections.Counter(ri)
          if conri['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_7 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=ri)
               retval_7.DoseFunctionParameters.DoseLevel = int(pdose*0.9)
               retval_7.DoseFunctionParameters.PercentVolume = 50    
               retval_7.DoseFunctionParameters.Weight = 5  
          else:
              if int(str(ri.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ri)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(ri.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15

   if len(cordls) !=0:
       for ci in cordls:
          if 'cm' not in roi_names:
            with CompositeAction('ROI Algebra (cm)'):
               retval_0 = patient.PatientModel.CreateRoi(Name="cm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
               retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [ci], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 })
               retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto") 
          conci=collections.Counter(ci)
          if conci['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
               retval_8.DoseFunctionParameters.DoseLevel = int(pdose*0.73)
               retval_8.DoseFunctionParameters.Weight = 30 
          else:
              if int(str(ci.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_7 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
                    retval_7.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_7.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_17 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ci)
                    retval_17.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_17.DoseFunctionParameters.EudParameterA = 150
                    retval_17.DoseFunctionParameters.Weight = 30
    
   if len(kidls) !=0:
       for ki in kidls:
          conki=collections.Counter(ki)
          if conki['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_9 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=ki)
               retval_9.DoseFunctionParameters.DoseLevel = int(pdose*0.2)
               retval_9.DoseFunctionParameters.PercentVolume = 40
               retval_9.DoseFunctionParameters.Weight = 5
                
            with CompositeAction('Add Optimization Function'):
               retval_10 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=ki)
               retval_10.DoseFunctionParameters.DoseLevel = int(pdose*0.333)
               retval_10.DoseFunctionParameters.PercentVolume = 22
               retval_10.DoseFunctionParameters.Weight = 5
          else:
              if int(str(ki.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ki)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(ki.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15
    
   if len(lungls) !=0:
       if len(lungls)==2:
          if "Lung-Z" not in roi_names:
            with CompositeAction('ROI Algebra (Lung-Z)'):  
                 retval_0 = patient.PatientModel.CreateRoi(Name="Lung-Z", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)     
                 retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [lungls[0], lungls[1]], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })  
                 retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
               # CompositeAction ends
       for lgi in lungls:
          conlgi=collections.Counter(lgi)
          if conlgi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_11 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_11.DoseFunctionParameters.DoseLevel = int(pdose*0.13)
               retval_11.DoseFunctionParameters.PercentVolume = 45
               retval_11.DoseFunctionParameters.Weight = 5
               
            with CompositeAction('Add Optimization Function'):
               retval_12 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_12.DoseFunctionParameters.DoseLevel = int(pdose*0.35)
               retval_12.DoseFunctionParameters.PercentVolume = 22
               retval_12.DoseFunctionParameters.Weight = 5
          else:
              if int(str(lgi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=lgi)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(lgi.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15

   if len(heartls) !=0:
       for hti in heartls:
          conhti=collections.Counter(hti)
          if conhti['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_13 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=hti)
               retval_13.DoseFunctionParameters.DoseLevel = int(pdose*0.5)
               retval_13.DoseFunctionParameters.PercentVolume = 30
               retval_13.DoseFunctionParameters.Weight = 5

            with CompositeAction('Add Optimization Function'):
               retval_14 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=hti)
               retval_14.DoseFunctionParameters.DoseLevel = int(pdose*0.67)
               retval_14.DoseFunctionParameters.PercentVolume = 22
               retval_14.DoseFunctionParameters.Weight = 5  

          else:
              if int(str(hti.split('_')[1]))!=0:
                   with CompositeAction('Add Optimization Function'):
                      retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=hti)
                      retval_10.DoseFunctionParameters.DoseLevel = int(str(hti.split('_')[1]))
                      retval_10.DoseFunctionParameters.EudParameterA = 1
                      retval_10.DoseFunctionParameters.Weight = 15

   if len(liverls) !=0:
       for lvri in liverls:
          conlvri=collections.Counter(lvri)
          if conlvri['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_15 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lvri)
               retval_15.DoseFunctionParameters.DoseLevel = int(pdose*0.2)
               retval_15.DoseFunctionParameters.PercentVolume = 40
               retval_15.DoseFunctionParameters.Weight = 5

            with CompositeAction('Add Optimization Function'):
               retval_16 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lvri)
               retval_16.DoseFunctionParameters.DoseLevel = int(pdose*0.33)
               retval_16.DoseFunctionParameters.PercentVolume = 22
               retval_16.DoseFunctionParameters.Weight = 5  

          else:
              if int(str(lvri.split('_')[1]))!=0:
                   with CompositeAction('Add Optimization Function'):
                      retval_16 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=lvri)
                      retval_16.DoseFunctionParameters.DoseLevel = int(str(lvri.split('_')[1]))
                      retval_16.DoseFunctionParameters.EudParameterA = 1
                      retval_16.DoseFunctionParameters.Weight = 15

   if len(rels) !=0:
       for rei in rels:
          with CompositeAction('Add Optimization Function'):
             retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=rei)
             retval_8.DoseFunctionParameters.DoseLevel = int(pdose*0.75)
             retval_8.DoseFunctionParameters.Weight = 30 

if 'BREASTCTRL.VMAT' in roi_names or 'BREASTCTRL.IMRT' in roi_names:

   if len(cordls) !=0:
       for ci in cordls:
          if 'cm' not in roi_names:
            with CompositeAction('ROI Algebra (cm)'):
               retval_0 = patient.PatientModel.CreateRoi(Name="cm", Color="Cyan", Type="Organ", TissueName=None, RoiMaterial=None)
               retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [ci], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 })
               retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto") 
          conci=collections.Counter(ci)
          if conci['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_8 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
               retval_8.DoseFunctionParameters.DoseLevel = int(pdose*0.73)
               retval_8.DoseFunctionParameters.Weight = 30 
          else:
              if int(str(ci.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_7 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=ci)
                    retval_7.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_7.DoseFunctionParameters.Weight = 50
                 with CompositeAction('Add Optimization Function'):
                    retval_17 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ci)
                    retval_17.DoseFunctionParameters.DoseLevel = int(str(ci.split('_')[1]))
                    retval_17.DoseFunctionParameters.EudParameterA = 150
                    retval_17.DoseFunctionParameters.Weight = 30
    
   if len(kidls) !=0:
       for ki in kidls:
          conki=collections.Counter(ki)
          if conki['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_9 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=ki)
               retval_9.DoseFunctionParameters.DoseLevel = int(pdose*0.2)
               retval_9.DoseFunctionParameters.PercentVolume = 40
               retval_9.DoseFunctionParameters.Weight = 5
                
            with CompositeAction('Add Optimization Function'):
               retval_10 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=ki)
               retval_10.DoseFunctionParameters.DoseLevel = int(pdose*0.333)
               retval_10.DoseFunctionParameters.PercentVolume = 22
               retval_10.DoseFunctionParameters.Weight = 5
          else:
              if int(str(ki.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=ki)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(ki.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15
    
   if len(lungls) !=0:
       if len(lungls)==2:
          if "Lung-Z" not in roi_names:
            with CompositeAction('ROI Algebra (Lung-Z)'):  
                 retval_0 = patient.PatientModel.CreateRoi(Name="Lung-Z", Color="Pink", Type="Organ", TissueName=None, RoiMaterial=None)     
                 retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [lungls[0], lungls[1]], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })  
                 retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
               # CompositeAction ends
       for lgi in lungls:
          conlgi=collections.Counter(lgi)
          if conlgi['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_11 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_11.DoseFunctionParameters.DoseLevel = int(pdose*0.13)
               retval_11.DoseFunctionParameters.PercentVolume = 45
               retval_11.DoseFunctionParameters.Weight = 5
               
            with CompositeAction('Add Optimization Function'):
               retval_12 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lgi)
               retval_12.DoseFunctionParameters.DoseLevel = int(pdose*0.35)
               retval_12.DoseFunctionParameters.PercentVolume = 22
               retval_12.DoseFunctionParameters.Weight = 5
          else:
              if int(str(lgi.split('_')[1]))!=0:
                 with CompositeAction('Add Optimization Function'):
                    retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=lgi)
                    retval_10.DoseFunctionParameters.DoseLevel = int(str(lgi.split('_')[1]))
                    retval_10.DoseFunctionParameters.EudParameterA = 1
                    retval_10.DoseFunctionParameters.Weight = 15

   if len(heartls) !=0:
       for hti in heartls:
          conhti=collections.Counter(hti)
          if conhti['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_13 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=hti)
               retval_13.DoseFunctionParameters.DoseLevel = int(pdose*0.5)
               retval_13.DoseFunctionParameters.PercentVolume = 30
               retval_13.DoseFunctionParameters.Weight = 5

            with CompositeAction('Add Optimization Function'):
               retval_14 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=hti)
               retval_14.DoseFunctionParameters.DoseLevel = int(pdose*0.67)
               retval_14.DoseFunctionParameters.PercentVolume = 22
               retval_14.DoseFunctionParameters.Weight = 5  

          else:
              if int(str(hti.split('_')[1]))!=0:
                   with CompositeAction('Add Optimization Function'):
                      retval_10 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=hti)
                      retval_10.DoseFunctionParameters.DoseLevel = int(str(hti.split('_')[1]))
                      retval_10.DoseFunctionParameters.EudParameterA = 1
                      retval_10.DoseFunctionParameters.Weight = 15

   if len(liverls) !=0:
       for lvri in liverls:
          conlvri=collections.Counter(lvri)
          if conlvri['_']==0:
            with CompositeAction('Add Optimization Function'):
               retval_15 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lvri)
               retval_15.DoseFunctionParameters.DoseLevel = int(pdose*0.2)
               retval_15.DoseFunctionParameters.PercentVolume = 40
               retval_15.DoseFunctionParameters.Weight = 5

            with CompositeAction('Add Optimization Function'):
               retval_16 = po.AddOptimizationFunction(FunctionType="MaxDVH", RoiName=lvri)
               retval_16.DoseFunctionParameters.DoseLevel = int(pdose*0.33)
               retval_16.DoseFunctionParameters.PercentVolume = 22
               retval_16.DoseFunctionParameters.Weight = 5  

          else:
              if int(str(lvri.split('_')[1]))!=0:
                   with CompositeAction('Add Optimization Function'):
                      retval_16 = po.AddOptimizationFunction(FunctionType="MaxEud", RoiName=lvri)
                      retval_16.DoseFunctionParameters.DoseLevel = int(str(lvri.split('_')[1]))
                      retval_16.DoseFunctionParameters.EudParameterA = 1
                      retval_16.DoseFunctionParameters.Weight = 15

with CompositeAction('Add Optimization Function'):
   retval_11 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName="B1")
   retval_11.DoseFunctionParameters.DoseLevel = int(pdose*0.8)
   retval_11.DoseFunctionParameters.Weight = 1 

with CompositeAction('Add Optimization Function'):
   retval_12 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName="B1.5")
   retval_12.DoseFunctionParameters.DoseLevel = int(pdose*0.7)
   retval_12.DoseFunctionParameters.Weight = 1 

with CompositeAction('Add Optimization Function'):
   retval_13 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName="B2")
   retval_13.DoseFunctionParameters.DoseLevel = int(pdose*0.5)
   retval_13.DoseFunctionParameters.Weight = 1

if (nob=='BST7' or nob=='BST4'):
      if "BSTP" not in roi_names:
          with CompositeAction('ROI Algebra (BSTP)'):
         
              retval_4 = patient.PatientModel.CreateRoi(Name="BSTP", Color="Cyan", Type="Ptv", TissueName=None, RoiMaterial=None)
                
              retval_4.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 2, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            
              retval_4.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
      with CompositeAction('Add Optimization Function'):
          retval_4 = po.AddOptimizationFunction(FunctionType="MinDose", RoiName="BSTP")
          retval_4.DoseFunctionParameters.DoseLevel = pdose   
          retval_4.DoseFunctionParameters.Weight = 2   

#patient.BodySite=machname + ' ' + stgleb + ' ' + pname

#patient.Save()

if optleb=='Y':
  patient = get_current("Patient")
  machine_db=get_current("MachineDB")
  examination = get_current("Examination")
  laps=['Lap1','Lap2','Lap3','Lap4']
  roi_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]

  dos=[]
  nfra=[]
  pdos=[]
  tarls=[]
  dosls=[]

  for m in roi_names:

     if patient.PatientModel.RegionsOfInterest[m].OrganData.OrganType == "Target":

         con=collections.Counter(m)
              
         if con['_']==2:
             pname=m
             nf=m.split('_')[1]
             dy=m.split('_')[2]
             tarls.append(m) 
             dos.append(int(dy))
             nfra.append(int(nf))
             dosls.append(int(dy))
         
         if con['_']==3:
             pname=m
             nf=m.split('_')[1]
             dy=m.split('_')[2]
             #tarls.append(m) 
             dos.append(int(dy))
             nfra.append(int(nf))
             #dosls.append(int(dy))

         if con['_']==1:   
             tarls.append(m)
             dostmp=m.split('_')[1]
             dosls.append(int(dostmp))

  pdose=max(dos)

  info=patient.QueryPlanInfo(Filter={'Name':'^{0}$'.format("plan")})
  patient.LoadPlan(PlanInfo=info[0])

  plan=patient.LoadPlan(PlanInfo=info[0])

  po=plan.PlanOptimizations[0]
  opt_param = po.OptimizationParameters
  rtmp_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
  for i in laps:
      if i in rtmp_names:
          with CompositeAction('Delete ROI (i)'):
              patient.PatientModel.RegionsOfInterest[i].DeleteRoi()
  retval_1 = patient.PatientModel.CreateRoi(Name=laps[0], Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
  po.RunOptimization()

  con2=collections.Counter(pname)
  if con2['_']==2:
     with CompositeAction('Add Optimization Function'):
        retval_1 = po.AddOptimizationFunction(FunctionType="MinDVH", RoiName=pname)
        retval_1.DoseFunctionParameters.DoseLevel = pdose
        retval_1.DoseFunctionParameters.PercentVolume = 97    
        retval_1.DoseFunctionParameters.Weight = 400

     with CompositeAction('Add Optimization Function'):
        retval_2 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName=pname)
        retval_2.DoseFunctionParameters.DoseLevel = int(pdose*1.085)
        retval_2.DoseFunctionParameters.Weight = 400
  if con2['_']==3:
     with CompositeAction('Add Optimization Function'):
        retval_1 = po.AddOptimizationFunction(FunctionType="MinDVH", RoiName=pname)
        retval_1.DoseFunctionParameters.DoseLevel = pdose
        retval_1.DoseFunctionParameters.PercentVolume = 97    
        retval_1.DoseFunctionParameters.Weight = 60
  rtmp_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
  for i in laps:
      if i in rtmp_names:
          with CompositeAction('Delete ROI (i)'):
              patient.PatientModel.RegionsOfInterest[i].DeleteRoi()
  retval_1 = patient.PatientModel.CreateRoi(Name=laps[1], Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
  po.RunOptimization()    

  if ("rx" not in roi_names):
    with CompositeAction('ROI Algebra (rx)'):

      retval_1 = patient.PatientModel.CreateRoi(Name="rx", Color="Yellow", Type="Organ", TissueName=None, RoiMaterial=None)

      retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.4, 'Inferior': 0.4, 'Anterior': 0.4, 'Posterior': 0.4, 'Right': 0.4, 'Left': 0.4 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
  
  with CompositeAction('Add Optimization Function'):
     retval_2 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName="rx")
     retval_2.DoseFunctionParameters.DoseLevel = pdose-40
     retval_2.DoseFunctionParameters.Weight = 50

  if ("pr" not in roi_names):
    with CompositeAction('ROI Algebra (pr)'):
 
      retval_3 = patient.PatientModel.CreateRoi(Name="pr", Color="Yellow", Type="Ptv", TissueName=None, RoiMaterial=None)

      retval_3.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [pname], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.4, 'Inferior': 0.4, 'Anterior': 0.4, 'Posterior': 0.4, 'Right': 0.4, 'Left': 0.4 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_3.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

  with CompositeAction('Add Optimization Function'):
     retval_4 = po.AddOptimizationFunction(FunctionType="MinDVH", RoiName="pr")
     retval_4.DoseFunctionParameters.DoseLevel = pdose+20
     retval_4.DoseFunctionParameters.PercentVolume = 100    
     retval_4.DoseFunctionParameters.Weight = 10

  if "DSSX" in roi_names:
     with CompositeAction('Add Optimization Function'):
        retval_5 = po.AddOptimizationFunction(FunctionType="MaxDose", RoiName="DSSX")
        retval_5.DoseFunctionParameters.DoseLevel = int(pdose*0.81)   
        retval_5.DoseFunctionParameters.Weight = 15
  rtmp_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
  for i in laps:
      if i in rtmp_names:
          with CompositeAction('Delete ROI (i)'):
              patient.PatientModel.RegionsOfInterest[i].DeleteRoi()
  retval_1 = patient.PatientModel.CreateRoi(Name=laps[2], Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
  po.RunOptimization()
  rtmp_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
  for i in laps:
      if i in rtmp_names:
          with CompositeAction('Delete ROI (i)'):
              patient.PatientModel.RegionsOfInterest[i].DeleteRoi()
  retval_1 = patient.PatientModel.CreateRoi(Name=laps[3], Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
  po.RunOptimization()
  
  #patient.Save()

else:
  pass
