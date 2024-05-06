from flask import Flask, render_template
import cv2
import numpy as np
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd

app = Flask(__name__)

# Route to display the heatmap
@app.route('/heatmap')
def heatmap():
    # Read and process the image
    img = cv2.imread('static/nighttimeIMAGE1.jpg')
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold_value = 127
    ret, thresh_img = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
    np_img = np.array(img)
    green_channel = np_img[:,:,1]
    sns.heatmap(green_channel)
    plt.savefig('static/heatmap.png')  # Save the heatmap as a static image
    plt.close()

    return render_template('heatmap.html')

# Route to display the choropleth map
@app.route('/choropleth')
def choropleth():
    # Load and process the GeoJSON file
    df = pd.read_csv('static/gdp.csv')
    state_average = dict(zip(df['State'], df['Average']))
    with open('static/gadm41_IND_1.json', 'r') as f:
        geojson_data = json.load(f)
    for feature in geojson_data['features']:
        state_name = feature['properties']['NAME_1']
        if state_name in state_average:
            feature['properties']['average'] = state_average[state_name]
        else:
            feature['properties']['average'] = None

    with open('static/gadm41_IND_1_with_average.json', 'w') as f:
        json.dump(geojson_data, f)

    gdf = gpd.read_file('static/gadm41_IND_1_with_average.json')
    scale_factor = 0.5
    vmin = gdf['average'].min()
    vmax = gdf['average'].max() * scale_factor

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    gdf.plot(column='average', ax=ax, legend=True, cmap='viridis', edgecolor='black', linewidth=0.5, vmin=vmin, vmax=vmax)
    plt.savefig('static/choropleth.png')  # Save the choropleth map as a static image
    plt.close()

    return render_template('choropleth.html')

if __name__ == '__main__':
    app.run(debug=True)
