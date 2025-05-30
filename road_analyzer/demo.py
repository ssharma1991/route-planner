from road_analyzer import RoadAnalyzer, BoundingBox

# Stanford University area
bbox = BoundingBox(
    left=-122.25,
    bottom=37.4,
    right=-122.1,
    top=37.5
)

print("\nInitializing RoadAnalyzer")
road_analyzer = RoadAnalyzer()
road_analyzer.add_bounding_box(bbox)

print("\nDownloading road data")
road_analyzer.fetch_road_data()
# road_analyzer.export_for_qgis('road_data.gpkg') # Geopackage can be opened in QGIS

print("\nAnalyzing road data")
road_analyzer.show_road_stats()
road_analyzer.simplify_road_classification()
# road_analyzer.plot_static_map()
road_analyzer.plot_interactive_map()
