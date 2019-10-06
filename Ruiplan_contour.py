# Script recorded 08 Feb 2017

#   RayStation version: 4.7.5.4
#   Selected patient: ...

import os
import time
import socket
import wpf
from System.Windows import *
from System.Windows.Controls import *
from os.path import join, getsize
import datetime
import shutil

class MyWindow(Window):

  def __init__(self):

     self.WindowStartupLocation=WindowStartupLocation.CenterScreen
     wpf.LoadComponent(self, 'RuiPlan_contour.xaml')

     section_list = ["HEAD","BODY","BREAST"]
     couch_list   = ["VARIAN","ELEKTA"]
     strategy_list= ["IMRT","VMAT"]

     self.SelectSC.ItemsSource = section_list
     self.SelectCH.ItemsSource = couch_list
     self.SelectStg.ItemsSource = strategy_list


  def ConfirmClicked(self, sender, event):

     ''' Gets the dose at the selected relative volume for the selected ROI '''
        
     sc_name  =  self.SelectSC.SelectedItem
     ch_name  =  self.SelectCH.SelectedItem
     stg_name =  self.SelectStg.SelectedItem

     if sc_name == "":
         raise Exception ("No Section Selected. Please check!!!")
         os._exit()
         return
     if ch_name == "":
        raise Exception ("No Couch Selected. Please check!!!")
        os._exit()
        return
     mg1 = float(self.Marg.Text)
        
     if mg1 > 1.5: 
        #maximum margin larger than 1.5cm is not allowed 
        return
     lenm=len(str(mg1))        
     if (mg1==0 or lenm==0):
         if sc_name=="HEAD":
            mg=0.5
         if sc_name=="BODY":
            mg=0.7
         if sc_name=="BREAST":
            mg=1.0
     else:
         mg=mg1
     
#     pswd=self.pwd.Password
#     if pswd.upper()==chr(65)+chr(67):
#        pass 
#     else:
#        raise Exception ("Wrong Password!!!")
#        os._exit()        
     with open("para_con","wb") as con:
        con.write(sc_name + '\r\n'+ str(mg)+'\r\n'+ ch_name + '\r\n' + stg_name + '\r\n')

     text = "CTV or GTV with margin {0} cm has been built."

     self.Ptext.Text = text.format(str(mg))

     self.RelVolPanel.Visibility = Visibility.Visible

  def CloseClicked(self, sender, event):

     self.DialogResult = True


# Run in RayStation
from connect import *
window = MyWindow()
window.ShowDialog()
patient = get_current("Patient")
examination = get_current("Examination")

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

#rois=[r.Name for r in patient.PatientModel.RegionsOfInterest]
#for roi in rois:
#    if  patient.PatientModel.StructureSets[examination.Name].RoiGeometries[roi].HasContours():
#        pass
#    else:
#        with CompositeAction('Delete ROI (roi)'):
#            patient.PatientModel.RegionsOfInterest[roi].DeleteRoi()
#
roi_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
#with CompositeAction('Apply image set properties'):
#  examination.EquipmentInfo.SetImagingSystemReference(ImagingSystemName="rtp2")

with open ('para_con' ,'r') as ptmp:
    lines=ptmp.readlines()
    section=lines[0][0:-1]
    marg=float(lines[1])
    couch=lines[2][0:-1]
    strategy=lines[3][0:-1]

ch_count=0
for ch in roi_names:
   n=ch[0:5].upper()
   if n=="COUCH":
      ch_count+=1
if ch_count==0:
  if couch == 'VARIAN':
     patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Varian Couch", SourceExaminationName="CT 1", SourceRoiNames=["CouchSurface", "CouchInterior"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
  elif couch == 'ELEKTA':
     patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Elekta Couch infinity", SourceExaminationName="CT 1", SourceRoiNames=["CouchSide", "CouchInterior", "CouchSurface"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
elif ch_count==2:
  if couch == 'VARIAN':
     pass
     #patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Varian Couch", SourceExaminationName="CT 1", SourceRoiNames=["CouchSurface", "CouchInterior"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
  elif couch == 'ELEKTA':
     for ch in roi_names:
         if "Couch" in ch:
            patient.PatientModel.RegionsOfInterest[ch].DeleteRoi()
     patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Elekta Couch infinity", SourceExaminationName="CT 1", SourceRoiNames=["CouchSide", "CouchInterior", "CouchSurface"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
elif ch_count==3:
  if couch == 'VARIAN':
     for ch in roi_names:
         if "Couch" in ch:
            patient.PatientModel.RegionsOfInterest[ch].DeleteRoi()
     patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Varian Couch", SourceExaminationName="CT 1", SourceRoiNames=["CouchSurface", "CouchInterior"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
  elif couch == 'ELEKTA':
     pass
     #patient.PatientModel.CreateStructuresFromTemplate(SourceTemplateName="Elekta Couch infinity", SourceExaminationName="CT 1", SourceRoiNames=["CouchSide", "CouchInterior", "CouchSurface"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, InitializationOption="AlignImageCenters")
if ch_count>3:
     pass
#with open ('xy.txt','w') as xy:
#    if couch == 'VARIAN':
#       xy.write(couch)
#    else:
#       xy.write("6")

tardict=["GTV","CTV","PGT","PTV","PCT","ITV"]
for d in roi_names:
   n=d[0:3].upper()
   if n in tardict:
     with CompositeAction('Apply ROI changes (d)'):

       patient.PatientModel.RegionsOfInterest[d].Type = "Ctv"

       patient.PatientModel.RegionsOfInterest[d].OrganData.OrganType = "Target"

       patient.PatientModel.RegionsOfInterest[d].SetRoiMaterial(Material=None)



   elif (n=="SKI" or n=="BOD") and len(d)<6:
     
     with CompositeAction('Apply ROI changes (d)'):
     
       #patient.PatientModel.RegionsOfInterest[d].Type = "External"
       
       patient.PatientModel.RegionsOfInterest[d].SetRoiMaterial(Material=None) 
       
     with CompositeAction('Create external (d)'):
    
       patient.PatientModel.RegionsOfInterest[d].CreateExternalGeometry(Examination=examination, ThresholdLevel=-250)
    
     with CompositeAction('Apply ROI changes (d)'):
     
       patient.PatientModel.RegionsOfInterest[d].Name = "skin"
   elif (n=="EXT") and len(d)<9:
     
     with CompositeAction('Apply ROI changes (d)'):
     
       #patient.PatientModel.RegionsOfInterest[d].Type = "External"
       
       patient.PatientModel.RegionsOfInterest[d].SetRoiMaterial(Material=None) 
       
     with CompositeAction('Create external (d)'):

       patient.PatientModel.RegionsOfInterest[d].CreateExternalGeometry(Examination=examination, ThresholdLevel=-250)

     with CompositeAction('Apply ROI changes (d)'):
     
       patient.PatientModel.RegionsOfInterest[d].Name = "skin"   

   elif (n=="COU") and d[0:5].upper()=='COUCH':
       pass
   else:

     with CompositeAction('Apply ROI changes (d)'):
  
       patient.PatientModel.RegionsOfInterest[d].SetRoiMaterial(Material=None)
  
         # CompositeAction ends 


poi_names=[r.Name for r in patient.PatientModel.PointsOfInterest]
  
if len(poi_names)==1:

   if poi_names[0]=="MK": 
      patient.PatientModel.PointsOfInterest['MK'].Type = "LocalizationPoint"

   else:
      patient.PatientModel.PointsOfInterest[poi_names[0]].Name = "MK"
   
      patient.PatientModel.PointsOfInterest['MK'].Type = "LocalizationPoint"

     
elif len(poi_names)==0:
   raise Exception ("No POI geometry in POIs list. Please check!!!")
else:
   for p in poi_names:  
      if p=="I1":
         patient.PatientModel.PointsOfInterest[p].Name = "MK"
   
         patient.PatientModel.PointsOfInterest['MK'].Type = "LocalizationPoint"

rooi=[]

for k in roi_names:
  rooi.append(k)

for i in rooi:
  if i[0:3].upper()=="GTV" or i[0:3].upper()=="ITV":
    srcroi=i
    rstroi="P"+i
    if rstroi not in rooi:
      
      with CompositeAction('ROI Algebra (rstroi)'):
        
        retval_0 = patient.PatientModel.CreateRoi(Name=rstroi, Color="Maroon", Type="Ptv", TissueName=None, RoiMaterial=None)
          
        retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["skin"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [srcroi], 'MarginSettings': { 'Type': "Expand", 'Superior': marg, 'Inferior': marg, 'Anterior': marg, 'Posterior': marg, 'Right': marg, 'Left': marg } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

  # CompositeAction ends 

  if i[0:3].upper()=="CTV":
    srcroi=i
    rstroi1="P"+i
    rstroi2="P"+i[1:] 
    if rstroi1 not in rooi:
       if rstroi2 not in rooi:
          with CompositeAction('ROI Algebra (rstroi2)'):
          
            retval_0 = patient.PatientModel.CreateRoi(Name=rstroi2, Color="Maroon", Type="Ptv", TissueName=None, RoiMaterial=None)
            
            retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["skin"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [srcroi], 'MarginSettings': { 'Type': "Expand", 'Superior': marg, 'Inferior': marg, 'Anterior': marg, 'Posterior': marg, 'Right': marg, 'Left': marg } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            
            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")     

ctrleb=section + "CTRL." + strategy

for ctrl in roi_names:
    if  "CTRL." in ctrl:
        patient.PatientModel.RegionsOfInterest[ctrl].DeleteRoi()
    else:
        pass

roi_names=[r.Name for r in patient.PatientModel.RegionsOfInterest]
if section=="HEAD" and ctrleb not in roi_names:
  retval_1 = patient.PatientModel.CreateRoi(Name=ctrleb, Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
if section=="BODY" and ctrleb not in roi_names:
  retval_1 = patient.PatientModel.CreateRoi(Name=ctrleb, Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)
if section=="BREAST" and ctrleb not in roi_names:
  retval_1 = patient.PatientModel.CreateRoi(Name=ctrleb, Color="Magenta", Type="Control", TissueName=None, RoiMaterial=None)

id=patient.PatientID
tm=time.strftime("%Y-%m-%d %H:%M:%S %A",time.localtime())
ct=tm+'  ' + hm + '  '+ id +' RuiPlan2'+ '\t\n'
with open ('count','a') as xy:
    xy.write(ct)
#patient.Save()

fdir='\\\Sql\dicom\\'
for i in os.listdir(fdir):
    if os.path.isdir(fdir+i):
       dateago=(datetime.datetime.now()-datetime.timedelta(hours=24))
       agostamp=int(time.mktime(dateago.timetuple()))
       mktime=int(os.path.getctime(fdir+i))
       if agostamp-mktime >0:
           shutil.rmtree(fdir+i)
       for root, dirs, files in os.walk(fdir+i):
           size=0
           size += sum([getsize(join(root,name)) for name in files])
           sm=round(float(size)/1024/1024,2)
           if sm <0.5:
              shutil.rmtree(fdir+i) 
