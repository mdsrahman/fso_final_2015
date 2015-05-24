
from xml.etree.cElementTree import iterparse
import geopy.distance
import numpy as np
import logging

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


class MapToGraphGenerator:
  '''
  takes a file path to the .osm file as input and 
  saves the generated adjacency graph in the output file path
  major steps:
  1. laod and parse the osm file
  2. bin the buildings
  3.  calculate the LOS and generate the graph
  4. save the graph in the output file
  fields:
  --------------
  building_lat: dictionary of latitudes of all buildings, 
                keyed by building id as found in the osm file
  self.building_lon: dictionary of longitudes of all buildings, 
                keyed by building id as found in the osm file
  max_lon, max_lat: maximum longitude and latitude, used to map to Euclidian coordinate
  min_lon, self.min_lat: minimum longitude and latitude, used to map to Euclidian coordinate
  '''
  def __init__(self, mapFilePath, outputFilePath):
    self.mapFilePath = mapFilePath
    self.outputFilePath = outputFilePath
    
    self.building_lat = None 
    self.building_lon = None 
    self.min_lat = None 
    self.min_lon = None 
    self.max_lat = None 
    self.max_lon =  None
    self.node_x = None
    self.node_y = None
    
    self.logger = logging.getLogger('logger')
    self.logger.addHandler(logging.StreamHandler())
    self.logger.setLevel(logging.DEBUG)
    
  def parseMapFile(self):
    '''
    parse the osm file and save the corner points (lat,lon) of buildings, also min and max lat+lon
    '''
    ways = {}
    tags = {}
    refs = []
    way_id = None
    lat= {}
    lon = {}
    self.building_lat = {}
    self.building_lon = {}
    self.max_lat = self.max_lon = -float('inf')
    self.min_lat = self.min_lon = float('inf')
    building_counter = 0
    
     
    context = iterparse(self.mapFilePath, events=("start", "end"))
  
    context = iter(context)
  
    # get the root element
    event, root = context.next()
    
    for event, elem in context:
        if event == 'start': continue
        if elem.tag == 'tag':
            tags[elem.attrib['k']] = elem.attrib['v']
        #-----------------------------------------------------#
        #              node processing
        #-----------------------------------------------------#
        elif elem.tag == 'node':
            osmid = int(elem.attrib['id'])
            lat[osmid] = float(elem.attrib['lat'])
            lon[osmid] = float(elem.attrib['lon'])
            tags = {}
        #-----------------------------------------------------#
        #              node ref i.e nd processing
        #-----------------------------------------------------#          
        elif elem.tag == 'nd':
            refs.append(int(elem.attrib['ref']))
        #-----------------------------------------------------#
        #              way_id  processing
        #-----------------------------------------------------# 
        elif elem.tag == 'way_id':
          if elem.attrib['role'] == 'outer':
            way_id = int(elem.attrib['ref'])
            #members.append((int(elem.attrib['ref']), elem.attrib['type'], elem.attrib['role']))
        #-----------------------------------------------------#
        #              way processing
        #-----------------------------------------------------# 
        elif elem.tag == 'way':
            osm_id = int(elem.attrib['id'])
            ways[osm_id] = refs
            if 'building' in tags.keys():
              blat_list = [lat[nid] for nid in refs]
              del blat_list[-1]
              blon_list = [lon[nid] for nid in refs]
              del blon_list[-1]
              self.building_lat[osm_id] = blat_list
              self.building_lon[osm_id] = blon_list
              self.max_lat = max(blat_list+[self.max_lat])
              self.max_lon = max(blon_list+[self.max_lon])
              self.min_lat = min(blat_list+[self.min_lat])
              self.min_lon = min(blon_list+[self.min_lon])
              building_counter +=1
              #print "DEBUG:building# ",building_counter
              #ways.append((osm_id, tags, refs)) 
            refs = []
            tags = {}
        #-----------------------------------------------------#
        #              relation processing
        #-----------------------------------------------------# 
        elif elem.tag == 'relation':
            osm_id = int(elem.attrib['id'])
            if 'building' in tags.keys() and way_id:
              #<-----process the ways right here
              blat_list = [lat[nid] for nid in ways[way_id]]
              del blat_list[-1]
              blon_list = [lon[nid] for nid in ways[way_id]]
              del blon_list[-1]
              self.building_lat[osm_id] = blat_list
              self.building_lon[osm_id] = blon_list
              self.max_lat = max(blat_list+[self.max_lat])
              self.max_lon = max(blon_list+[self.max_lon])
              self.min_lat = min(blat_list+[self.min_lat])
              self.min_lon = min(blon_list+[self.min_lon])
              building_counter +=1
              #print "DEBUG:building# ",building_counter
              #relations.append((osm_id, tags, members))
            way_id = None
            tags = {}
        root.clear()
  
  def transformToCartesianCoord(self):
    '''
    transform the lat, lon of buildings into Cartesian Coord (x,y) 
    and save it in building_x, building_y dicts indexed by building id as set in osm file
    '''
    self.building_x = {}
    self.building_y = {}
    self.max_x = self.max_y = -float('inf')
    
    for bindx, blats in self.building_lat.iteritems():
      self.building_x[bindx] = []
      self.building_y[bindx] = []
      blons = self.building_lon[bindx]
      for blat, blon in zip(blats, blons):
        xy = geopy.Point(blat,blon)
        x_ref = geopy.Point(self.min_lat, blon)
        y_ref = geopy.Point(blat, self.min_lon)
        x = geopy.distance.distance(xy, x_ref).m
        y = geopy.distance.distance(xy, y_ref).m
        self.building_x[bindx].append(x)
        self.building_y[bindx].append(y)
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)
    del self.building_lat
    del self.building_lon
  
  def selectNodes(self):
    '''
    select nodes from building corner points (x,y)
    either choose all the nodes or some subsets of those to make the 
    later computation faster
    '''
    self.node_x=[]
    self.node_y=[]
    for bid in self.building_x:
      self.node_x.extend(self.building_x[bid])
      self.node_y.extend(self.building_y[bid])
      
  def debugGenerateVisualGraph(self):
    patches = [] 
    for bid, bxs in self.building_x.iteritems():
      #print "bid:",i,"------------------------------" 
      bys = self.building_y[bid]
      pcoord = np.asarray(zip(bxs, bys), dtype = float)
      polygon = Polygon(pcoord, fc='grey')
      #polygon.set_facecolor('none')
      patches.append(polygon) 
      
    
    fig, ax = plt.subplots()
    
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)     
    
    ax.autoscale(enable=True, axis = 'both', tight= True)
    ax.set_aspect('equal', 'box')
    plt.show()
    return 
  
  def debugPrintSummary(self):
    self.logger.info("Map File Path:"+str(self.mapFilePath))
    self.logger.info("Total Buildings:"+str(len(self.building_x)))
    self.logger.info("Total Corner Points:"+str(len(self.node_x)))
  def generateMapToGraph(self):
    '''
    complete all the steps of generating graph form osm map in this method
    all other methods are called in here
    Major Steps:
    1. parse the xml osm file map and store the building corner points lat, lon
    2. transform the building corner points(lat, lon) to Euclidian coord (x,y)
    3. select nodes, from building corner points (x,y), either all of those or some subset of those
      for example discarding all points within 20m of a chosen points etc.
    4. bin the buildings according to their corner points and interval values
    5. calculate the LOS among selected points and save the graph
    '''
    self.parseMapFile()
    self.transformToCartesianCoord()
    self.selectNodes()
    
    
    
    