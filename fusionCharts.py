import re
from functools import cmp_to_key

class fusionChart:
    """FusionChart Python Class"""
    
    def __init__(self, chart_type='multi_combi', width=500, height=350, fusion_basedir='/fusioncharts/js') :
        self.chart_type = chart_type
        self.width = width
        self.height = height
        self.fusion_basedir = fusion_basedir
        
        # Set some other defaults. These will typically be set later using setChartProperties
        self.series_data = {}
        self.series_attributes = {}
        self.series_links = {}
        self.vlines = {}
        self.hlines = {}
        self.color_array = [ "ff9900",   "7951cc",   "ef2f41",   "66cc66",
                                    "c2b00f",   "FFA500",   "A9A9A9",   "E1E1E1",
                                    "00FFFF",   "FFC0CB",   "808080",
                                    "FFFF00",   "000000",
                                    "FF0000",   "0000FF",   "008000",   "CCCCFF",
                                    "FF00FF",   "FFA500",   "A9A9A9",   "E1E1E1",
                                    "00FFFF",   "FFC0CB",   "808080",
                                    "FFFF00",   "000000"]

        # These are some default attributes for the <chart> tag
        # These or any new attribute can be set using setChartAttributes(). 
        # Other useful tags that should be defined by caller:
        # caption xAxisName, yAxisName, PYAxisName, SYAxisName
        self.chart_tag_attributes =  {
                                        "palette" : 2,
                                        "showPercentageValues" : 1,
                                        "showValues" : 1,
                                        "formatNumberScale" : 0,
                                        "useRoundEdges" : 1,
                                        "rotateLabels" : 1,
                                        "slantLabels" : 1, 
                                        "showAlternateHGridColor" : 1,
                                        "anchorRadius" : 2,
                                        "useRoundEdges" : 1,
                                        "showColumnShadow" : 0,
                                        "showAlternateHGridColor" : 1,
                                        "showExportDataMenuItem" : 1
                                        }

    # Set attributes for the chart tag
    # Input is a dictionary of attribute value pairs
    def setChartTagAttributes (self, params) :
        for attr, value in params.items():
            self.chart_tag_attributes[attr] = value

    # Name: addDataSeries()
    # Description: Added a data series to the chart.
    # Input Parameters:
    #     SERIES_NAME: (required) Unique name of a series.
    #                  This makes more sense for multiple series data but is currently required for all chart types
    #     SERIES_DATA: (required) Dictionary of labels/values
    #     SERIES_ATTRIBUTES: (optional) Dictionary of attribute/value pair string that will be used
    #                        in the <dataset> tag. Things like color can be overridden using this.
    #                        Currently only applicable to multi-series charts
    #     SERIES_LINKS: (optional) Dictionary of labels/links.
    #                   Individual data points can be linked to URLs using this
    def addDataSeries (self, series_name, series_data, series_attributes={}, series_links={}):
        self.series_data[series_name] = series_data
        self.series_attributes[series_name] = series_attributes
        self.series_links[series_name] = series_links

    # Name: addVlines()
    # Description: Added vertical lines to graph.
    # Input Parameters:
    #     VLINE_DATA: (required) Pointer to a hash of labels/attribute
    def addVlines (self, vlines):
        self.vlines = vlines

    # Name: addHlines()
    # Description: Add horizontal lines to graph.
    # Input Parameters:
    #     HLINE_DATA: (required) Pointer to a hash of label/attributes
    def addHlines (self, hlines):
        self.hlines = hlines

    def getXML (self):
        xml = ''
        chart_type = self.chart_type
        
        chart_tag_attrs = ''
        for attr, value in self.chart_tag_attributes.items():
            chart_tag_attrs = chart_tag_attrs + " %s='%s'" % (attr, value)
    
        if (chart_type == "pie" or chart_type == "column" or chart_type == "line" or chart_type == "area") :
            # Simple graph, labels and values are together and there is just one data series, pick first
            series_name = list(self.series_data.keys())[0]
            xml = "<chart " + chart_tag_attrs + " >\n"
            series_data_name_sorted = list(self.series_data[series_name].keys())
            series_data_name_sorted.sort(key=cmp_to_key(self.sortfn))
            for data_key in series_data_name_sorted:
                value = self.series_data[series_name][data_key]
                data_key_display = re.sub (r'^#\d+\.', '', data_key)
                try:
                    link_str = "link='%s'" % (self.series_links[series_name][data_key],)
                except:
                    link_str = ''
                xml +=  "<set label='%s' value='%s' %s/> \n" % (data_key_display, value, link_str)
            xml += "</chart>\n"
        elif re.search (r'multi', chart_type, re.I) :
            # Complex graph - usually multiple series with optional secondary Y-axis
            max_value = 0
            one_series = ""
            xml_lineset = ''
            #if re.search ('multi_stacked', chart_type):
            if chart_type == 'multi_stacked' or chart_type == 'multi_stacked_dy':
                xml += "<dataset>" 
            counter_series = 0;
            series_data_sorted = list(self.series_data.keys())
            series_data_sorted.sort(key=cmp_to_key(self.sortfn))
            # If there is no data, no point in continuing
            if len(series_data_sorted) == 0:
                return ''
            for series_name in series_data_sorted:
                series_display = re.sub (r'^#\d+\.', '', series_name)
                dataset_tag = "dataset"
                renderas = "" 
                attributes = ""
                
                for attr_name, attr_value in self.series_attributes[series_name].items():
                    attributes += " %s='%s'" % (attr_name, attr_value)
                    if re.search ('renderas', attr_name, re.I):
                        if (re.search('line', attr_value, re.I) and re.search('multi_stacked', chart_type, re.I)):
                            dataset_tag = "lineset"
    
                # Check if color has been overwridden using the series_attribute hash else use the array from chart attributes  
                if ('color' not in self.series_attributes[series_name]) :
                    if len(self.color_array) > 0:
                        attributes += " color='%s'" % self.color_array[counter_series]
                xml_tmp = "<%s seriesName='%s' %s> \n" % (dataset_tag, series_display, attributes)
                series_data_name_sorted = list(self.series_data[series_name].keys())
                series_data_name_sorted.sort(key=cmp_to_key(self.sortfn))
                for data_key in series_data_name_sorted: # TODO: Needs to be sorted
                    value = self.series_data[series_name][data_key]
                    try:
                        link_str = "link='%s'" % self.series_links[series_name][data_key]
                    except:
                        link_str = ''
                    xml_tmp += "<set value='%s' %s /> \n" % (value, link_str)
                    if (value != '' and value > max_value):
                        max_value = value 
                xml_tmp += "</%s> \n" % (dataset_tag,)
                
                #Linesets need to be added outside of all datasets, so if
                # lineset, keep in a variable to be added later
                if re.search ('lineset', dataset_tag):
                    xml_lineset += xml_tmp
                    counter_series += 1
                else:
                    xml += xml_tmp;
                    counter_series += 1
    
                # remember name of any one series. Will need to build categories later 
                one_series = series_name
    
            #if re.search ('multi_stacked', chart_type):
            if chart_type == 'multi_stacked' or chart_type == 'multi_stacked_dy':
                xml += "</dataset>"  
            xml += xml_lineset
    
            # Check if a hline has been specified
            if len(self.hlines) > 0 :
                xml += "<trendLines>"
                for trend_key in self.hlines.keys():
                    attributes = ''
                    for attr, value in self.hlines[trend_key].items():
                        attributes += " %s='%s'" % (attr, value)
                    xml += "<line displayValue='%s' %s />" % (trend_key, attributes)
                xml += "</trendLines>"
    
            xml += "<categories>"
            one_series_sorted = list(self.series_data[one_series].keys())
            one_series_sorted.sort(key=cmp_to_key(self.sortfn))
            for data_key in one_series_sorted: # TODO: needs to sort
                # Check if a vline has been specified for this label
                if data_key in self.vlines:
                    attributes = ''
                    for attr, value in self.vlines[data_key].items():
                        attributes += " %s='%s'" % (attr, value)
                    xml += "<vline %s/>" % (attributes,)
                data_key_display = re.sub (r'^#\d+\.', '', data_key);
                xml += "<category label='%s'/> \n" % (data_key_display,)
            xml += "</categories>"
            xml += "</chart>\n"
            
            try:
                max_value = int(max_value * 1.1)
            except:
                max_value = 0
            max_value = max_value + 10 - (max_value % 10)
            xml_header = "<chart %s >\n" % (chart_tag_attrs,)
            xml = xml_header + xml
        return (xml); 
    
    # Name: getHTML()
    # Description: Generate the HTML and JS code required to render the graph
    #              This will include the div container as well as the JS calls to FusionCharts.
    #              By default the XML will be generated "inline". For large files, user may want to 
    #              call getXML directly and save somewhere. The XML_URL can then be passed to this function
    # Input Parameters:
    #       ID: (required) the id for the div tag to be generated. It should be unique within the HTML doc
    #       DIV_PARAMS: (optional) This string will be added as-is to the div tag
    #                              use it set styles etc. 
    #       JS_ONLY: (optional) Dont generate any div tag or script tags. Caller will generate their own using the ID specified
    #       XML_URL: (optional) The URL where previously generated xml file is stored. If not specified,
    #                it will be automatically generated inline in the HTML  
    def getHTML (self, chartid, div_params='', js_only=0, xml_url=''):
        chart_type = self.chart_type
        graph_swf = "Column2D.swf"
        if (chart_type == "multi") :
            graph_swf = "MSColumn2D.swf"
        elif (chart_type == "multi_combi") :
            graph_swf = "MSCombi2D.swf"
        elif (chart_type == "multi_combi_dy") :
            graph_swf = "MSCombiDY2D.swf"
        elif (chart_type == "multi_stacked") :
            graph_swf = "MSStackedColumn2D.swf"
        elif (chart_type == "multi_stacked_area") :
            graph_swf = "StackedArea2D.swf"
        elif (chart_type == "multi_zoomline") :
            graph_swf = "ZoomLine.swf"
        elif (chart_type == "pie") :
            graph_swf = "Pie2D.swf"
        elif (chart_type == "area") :
            graph_swf = "Area2D.swf"
        elif (chart_type == "line") :
            graph_swf = "Line.swf";
        
        html = ''
        if (not js_only) :
            html += "<div id='%s' %s>Loading Graph</div>\n" % (chartid, div_params)
            html += "<script type='text/javascript'>\n"
        #html += "FusionCharts.setCurrentRenderer('javascript');\n"
        html += """var myChart_%s = new FusionCharts({
                    swfUrl: '%s/%s', 
                    width: '%s',
                    height: '%s',
                    debugMode : false
                    });\n""" % (chartid, self.fusion_basedir, graph_swf, self.width, self.height)
        if (xml_url != ''):
            html += "myChart_%s.setDataURL(escape('%s'));\n" % (chartid, xml_url)
        else :
            strXML = self.getXML()
            strXML = re.sub ("\n", " ", strXML)
            html += "myChart_%s.setXMLData(\"%s\");\n" % (chartid, strXML)
        html += "myChart_%s.render('%s');\n" % (chartid, chartid)
        if (not js_only) :
            html += "</script>\n"
        return (html)
    
    def getHTMLheader (self):
        html = "<script type=text/JavaScript src=%s/fusioncharts.js></script>" % (self.fusion_basedir,)
        return html;
    
    def sortfn (self, a, b):
        # Version Strings?
        ma=re.search (r'(\d+)\.(\d+)\.(\d+)\.*(\d*)', a)
        mb=re.search (r'(\d+)\.(\d+)\.(\d+)\.*(\d*)', b)
        if (ma and mb):
            a_padded = ''
            b_padded = ''
            for grp in ma.groups():
                if grp:
                    a_padded += "%03d" % (int(grp))
            for grp in mb.groups():
                if grp:
                    b_padded += "%03d" % (int(grp))
            #a_padded = "%03d%03d%03d%03d" % (int(ma.group(1)),int(ma.group(2)),int(ma.group(3)),int(ma.group(4)))
            #b_padded = "%03d%03d%03d%03d" % (int(mb.group(1)),int(mb.group(2)),int(mb.group(3)),int(mb.group(4)))
            #print "Using $b_padded and $a_padded <br>\n";
            if a_padded > b_padded: return 1
            if a_padded < b_padded: return -1
            return 0
        elif re.search (r'^-?\d+$', a) and re.search (r'^-?\d+$', b): 
            # Numbers
            return int(a) - int(b)
        elif re.search (r'^\d+%$', a) and re.search (r'^\d+%$', b):
            # Percentage
            a = re.sub ('%$', '', a)
            b = re.sub ('%$', '', b)
            return int(a) - int(b)
        elif re.search (r'^#\d+\.', a) and re.search (r'^#\d+\.', b):
            # Numbers added to front of keys for sorting
            a = re.search ('^#(\d+)\.', a).group(1)
            b = re.search ('^#(\d+)\.', b).group(1)
            return int(a) - int(b)
     
        # Normal string compare
        if a > b: return 1
        if a < b: return -1
        return 0

    
