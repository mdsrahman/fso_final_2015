
from xml.etree.cElementTree import iterparse
from __builtin__ import None

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
  building_lon: dictionary of longitudes of all buildings, 
                keyed by building id as found in the osm file
  max_lon, max_lat: maximum longitude and latitude, used to map to Euclidian coordinate
  min_lon, self.min_lat: minimum longitude and latitude, used to map to Euclidian coordinate
  '''
  def __init__(self, mapFilePath, outputFilePath):
    self.mapFilePath = mapFilePath
    self.outputFilePath = outputFilePath
    
    self.building_lat = None 
    self.building_lon = None 
    self.self.min_lat = None 
    self.min_lon = None 
    self.max_lat = None 
    self.max_lon =  None
    
  def parse(self):
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
