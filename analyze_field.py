import pandas as pd
from simple_ndvi import calculate_ndvi
from satellite_downloader import download_sentinel_image

def analyze_parcels(df_parcels):
    results = []
    for idx, row in df_parcels.iterrows():
        red_path, nir_path = download_sentinel_image(row['lat'], row['lon'], 'data/satellite_images')
        ndvi_path = f"data/satellite_images/ndvi_{idx}.tif"
        calculate_ndvi(nir_path, red_path, ndvi_path)
        results.append({'id': row['id'], 'ndvi_path': ndvi_path})
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = pd.read_csv('data/satellite_parcels.csv')  # fichier existant ou réel
    df_result = analyze_parcels(df)
    df_result.to_csv('data/satellite_ndvi_results.csv', index=False)
    print("Analysis completed and saved.")
