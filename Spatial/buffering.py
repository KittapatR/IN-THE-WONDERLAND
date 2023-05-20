from qgis.utils import iface
from qgis import processing
import glob
from qgis.PyQt.QtCore import QVariant


mc = iface.mapCanvas() 
inputlayer = glob.glob("C:/ECT/new_datasets/Constituencies/Province/clipped/*.shp")

for each_file in inputlayer:
    max_y = -1e6
    min_y = 1e6
    vectorlayer = QgsVectorLayer(each_file)
    vert = []
    for feature in vectorlayer.getFeatures():
        multipolygons = feature.geometry().asMultiPolygon()
        for polygon in multipolygons:
            for points in polygon:
                vert += points
                
    for vertex in vert:
        if vertex[1] > max_y: max_y = vertex[1]
        if vertex[1] < min_y: min_y = vertex[1]
        
    totalArea = (max_y - min_y)
    print(totalArea, max_y, min_y)

    processing.run("native:buffer", {'INPUT': each_file,
                  'DISTANCE': totalArea / 5 * 0.01,
                  'SEGMENTS': 10,
                  'DISSOLVE': False,
                  'END_CAP_STYLE': 1,
                  'JOIN_STYLE': 0,
                  'MITER_LIMIT': 10,
                  'OUTPUT': "C:/ECT/Buffered/" + each_file.split("\\")[-1]})
                  
    processing.run("saga:polygonselfintersection", {'POLYGONS': "C:/ECT/Buffered/" + each_file.split("\\")[-1],
        'ID': 'P_name',
        'INTERSECT': "C:/ECT/Buffered/intersected_" + each_file.split("\\")[-1]
        })
        
    last_vectorlayer = QgsVectorLayer("C:/ECT/Buffered/intersected_" + each_file.split("\\")[-1])
    vl = QgsVectorLayer("MultiPolygon", "temp", "memory")
    pr = vl.dataProvider()
    pr.addAttributes([QgsField("P_name", QVariant.String),
                      QgsField("CONS_no",  QVariant.Int)])
    vl.updateFields()
    
    for feature in last_vectorlayer.getFeatures():
        if feature.attributes()[1] != 0:
            f = QgsFeature()
            f.setGeometry(feature.geometry())
            f.setAttributes([each_file.split("\\")[-1].split("_")[-1][:-4], feature.attributes()[1]])
            pr.addFeature(f)
            vl.updateExtents()
            
    QgsVectorFileWriter.writeAsVectorFormat(vl,"C:/ECT/Final display/" + each_file.split("\\")[-1],"utf-8",vl.crs(),"ESRI Shapefile")
    
    processing.run("native:simplifygeometries", {'INPUT':"C:/ECT/Final display/" + each_file.split("\\")[-1],'METHOD':0,'TOLERANCE':0.001,'OUTPUT':"C:/ECT/Final display/simplified_" + each_file.split("\\")[-1]})
    processing.run("native:smoothgeometry", {'INPUT':"C:/ECT/Final display/simplified_" + each_file.split("\\")[-1],'ITERATIONS':3,'OFFSET': totalArea / 2 * 0.25,'MAX_ANGLE':180,'OUTPUT':"C:/ECT/Final display/rounded_" + each_file.split("\\")[-1]})
    processing.run("native:deleteholes", {'INPUT':"C:/ECT/Final display/rounded_" + each_file.split("\\")[-1],'MIN_AREA':1,'OUTPUT':"C:/ECT/Final display/final_" + each_file.split("\\")[-1]})