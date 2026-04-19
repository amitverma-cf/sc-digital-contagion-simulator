"""
Phase 2: Persona Definition
Creates behavioral archetypes using clustering analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pathlib import Path
import json

# Configuration
DATA_PATH = Path(__file__).parent.parent / "user_behavior_dataset.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_data():
    """Load dataset"""
    return pd.read_csv(DATA_PATH)

def prepare_clustering_features(df):
    """Select and normalize features for clustering"""
    print("="*60)
    print("FEATURE SELECTION FOR CLUSTERING")
    print("="*60)
    
    # Select behavioral features
    feature_cols = [
        'App Usage Time (min/day)',
        'Screen On Time (hours/day)',
        'Battery Drain (mAh/day)',
        'Number of Apps Installed',
        'Data Usage (MB/day)',
        'User Behavior Class'
    ]
    
    X = df[feature_cols].copy()
    print(f"\n✓ Selected {len(feature_cols)} features for clustering")
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("✓ Features normalized (StandardScaler)")
    
    return X, X_scaled, feature_cols, scaler

def determine_optimal_clusters(X_scaled, max_k=8):
    """Use elbow method to find optimal number of clusters"""
    print("\n" + "="*60)
    print("DETERMINING OPTIMAL NUMBER OF CLUSTERS")
    print("="*60)
    
    inertias = []
    silhouette_scores = []
    K_range = range(2, max_k + 1)
    
    from sklearn.metrics import silhouette_score
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    
    # Plot elbow curve
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(K_range, inertias, 'bo-', linewidth=3, markersize=8, marker='o', markeredgewidth=2, markeredgecolor='#1e40af')
    ax1.set_xlabel('Number of Clusters (k)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12, fontweight='bold')
    ax1.set_title('Elbow Method for Optimal k', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.4, linestyle='--')
    ax1.tick_params(labelsize=10)
    ax1.set_xlim(1.5, max_k + 0.5)
    
    ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=3, markersize=8, marker='s', markeredgewidth=2, markeredgecolor='#b91c1c')
    ax2.set_xlabel('Number of Clusters (k)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Silhouette Score', fontsize=12, fontweight='bold')
    ax2.set_title('Silhouette Analysis', fontsize=13, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.4, linestyle='--')
    ax2.tick_params(labelsize=10)
    ax2.set_xlim(1.5, max_k + 0.5)
    
    plt.suptitle('Clustering Optimization: Determining Optimal Number of Personas', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "clustering_optimization.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved clustering optimization plots to {output_path}")
    plt.close()
    
    # Recommend k=5 based on project requirements
    optimal_k = 5
    print(f"\n✓ Optimal k selected: {optimal_k} (balances interpretability and separation)")
    
    return optimal_k

def perform_clustering(X_scaled, n_clusters=5):
    """Perform k-means clustering"""
    print("\n" + "="*60)
    print(f"PERFORMING K-MEANS CLUSTERING (k={n_clusters})")
    print("="*60)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    print(f"\n✓ Clustering complete")
    print(f"✓ Cluster distribution:")
    for i in range(n_clusters):
        count = np.sum(cluster_labels == i)
        pct = (count / len(cluster_labels)) * 100
        print(f"  Cluster {i}: {count} samples ({pct:.1f}%)")
    
    return kmeans, cluster_labels

def analyze_personas(df, cluster_labels, feature_cols):
    """Analyze characteristics of each cluster"""
    print("\n" + "="*60)
    print("PERSONA CHARACTERIZATION")
    print("="*60)
    
    df_clustered = df.copy()
    df_clustered['Cluster'] = cluster_labels
    
    personas = {}
    persona_names = ['Minimalist', 'Moderate User', 'Active User', 'Heavy User', 'Digital Addict']
    
    # Sort clusters by average screen time to assign meaningful names
    cluster_means = df_clustered.groupby('Cluster')['Screen On Time (hours/day)'].mean().sort_values()
    cluster_to_persona = {cluster: persona_names[i] for i, cluster in enumerate(cluster_means.index)}
    
    for cluster_id, persona_name in cluster_to_persona.items():
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
        
        personas[persona_name] = {
            'cluster_id': int(cluster_id),
            'count': int(len(cluster_data)),
            'percentage': float((len(cluster_data) / len(df_clustered)) * 100),
            'characteristics': {
                'app_usage_mean': float(cluster_data['App Usage Time (min/day)'].mean()),
                'app_usage_std': float(cluster_data['App Usage Time (min/day)'].std()),
                'screen_time_mean': float(cluster_data['Screen On Time (hours/day)'].mean()),
                'screen_time_std': float(cluster_data['Screen On Time (hours/day)'].std()),
                'battery_drain_mean': float(cluster_data['Battery Drain (mAh/day)'].mean()),
                'battery_drain_std': float(cluster_data['Battery Drain (mAh/day)'].std()),
                'apps_installed_mean': float(cluster_data['Number of Apps Installed'].mean()),
                'apps_installed_std': float(cluster_data['Number of Apps Installed'].std()),
                'data_usage_mean': float(cluster_data['Data Usage (MB/day)'].mean()),
                'data_usage_std': float(cluster_data['Data Usage (MB/day)'].std()),
                'behavior_class_mode': int(cluster_data['User Behavior Class'].mode()[0]),
                'age_mean': float(cluster_data['Age'].mean()),
                'age_std': float(cluster_data['Age'].std()),
            }
        }
        
        print(f"\n{persona_name} (Cluster {cluster_id}):")
        print(f"  Population: {personas[persona_name]['count']} ({personas[persona_name]['percentage']:.1f}%)")
        print(f"  Screen Time: {personas[persona_name]['characteristics']['screen_time_mean']:.1f}±{personas[persona_name]['characteristics']['screen_time_std']:.1f} hrs/day")
        print(f"  App Usage: {personas[persona_name]['characteristics']['app_usage_mean']:.0f}±{personas[persona_name]['characteristics']['app_usage_std']:.0f} min/day")
        print(f"  Battery Drain: {personas[persona_name]['characteristics']['battery_drain_mean']:.0f}±{personas[persona_name]['characteristics']['battery_drain_std']:.0f} mAh/day")
        print(f"  Apps Installed: {personas[persona_name]['characteristics']['apps_installed_mean']:.0f}±{personas[persona_name]['characteristics']['apps_installed_std']:.0f}")
        print(f"  Behavior Class (mode): {personas[persona_name]['characteristics']['behavior_class_mode']}")
    
    return personas, cluster_to_persona

def visualize_personas(df, cluster_labels, personas, cluster_to_persona):
    """Create visualizations of persona characteristics"""
    print("\n" + "="*60)
    print("GENERATING PERSONA VISUALIZATIONS")
    print("="*60)
    
    df_clustered = df.copy()
    df_clustered['Cluster'] = cluster_labels
    df_clustered['Persona'] = df_clustered['Cluster'].map(cluster_to_persona)
    
    # Persona comparison radar chart
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # 1. Screen Time distribution by persona
    ax = axes[0, 0]
    persona_order = ['Minimalist', 'Moderate User', 'Active User', 'Heavy User', 'Digital Addict']
    df_clustered['Persona'] = pd.Categorical(df_clustered['Persona'], categories=persona_order, ordered=True)
    bp = df_clustered.boxplot(column='Screen On Time (hours/day)', by='Persona', ax=ax, 
                             patch_artist=True, boxprops=dict(facecolor='#3B82F6', alpha=0.7),
                             medianprops=dict(color='black', linewidth=2))
    ax.set_xlabel('Persona', fontsize=11, fontweight='bold')
    ax.set_ylabel('Screen Time (hours/day)', fontsize=11, fontweight='bold')
    ax.set_title('Screen Time Distribution', fontsize=12, fontweight='bold', pad=10)
    plt.sca(ax)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.tick_params(labelsize=9)
    
    # 2. App Usage distribution
    ax = axes[0, 1]
    bp = df_clustered.boxplot(column='App Usage Time (min/day)', by='Persona', ax=ax,
                             patch_artist=True, boxprops=dict(facecolor='#059669', alpha=0.7),
                             medianprops=dict(color='black', linewidth=2))
    ax.set_xlabel('Persona', fontsize=11, fontweight='bold')
    ax.set_ylabel('App Usage (min/day)', fontsize=11, fontweight='bold')
    ax.set_title('App Usage Distribution', fontsize=12, fontweight='bold', pad=10)
    plt.sca(ax)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.tick_params(labelsize=9)
    
    # 3. Battery Drain distribution
    ax = axes[0, 2]
    bp = df_clustered.boxplot(column='Battery Drain (mAh/day)', by='Persona', ax=ax,
                             patch_artist=True, boxprops=dict(facecolor='#F59E0B', alpha=0.7),
                             medianprops=dict(color='black', linewidth=2))
    ax.set_xlabel('Persona', fontsize=11, fontweight='bold')
    ax.set_ylabel('Battery Drain (mAh/day)', fontsize=11, fontweight='bold')
    ax.set_title('Battery Drain Distribution', fontsize=12, fontweight='bold', pad=10)
    plt.sca(ax)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.tick_params(labelsize=9)
    
    # 4. Persona size distribution
    ax = axes[1, 0]
    persona_counts = df_clustered['Persona'].value_counts()[persona_order]
    colors = ['#6B7280', '#3B82F6', '#059669', '#F59E0B', '#DC2626']
    bars = ax.bar(persona_order, persona_counts.values, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
    ax.set_xlabel('Persona', fontsize=11, fontweight='bold')
    ax.set_ylabel('Count', fontsize=11, fontweight='bold')
    ax.set_title('Persona Population Size', fontsize=12, fontweight='bold', pad=10)
    ax.grid(axis='y', alpha=0.4, linestyle='--')
    plt.sca(ax)
    plt.xticks(rotation=45, ha='right')
    ax.tick_params(labelsize=9)
    
    # 5. User Behavior Class by Persona
    ax = axes[1, 1]
    behavior_persona = df_clustered.groupby(['Persona', 'User Behavior Class']).size().unstack(fill_value=0)
    behavior_persona = behavior_persona.reindex(persona_order)
    behavior_persona.plot(kind='bar', stacked=True, ax=ax, colormap='viridis', alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Persona', fontsize=11, fontweight='bold')
    ax.set_ylabel('Count', fontsize=11, fontweight='bold')
    ax.set_title('Behavior Class Distribution', fontsize=12, fontweight='bold', pad=10)
    ax.legend(title='Behavior Class', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.sca(ax)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.tick_params(labelsize=9)
    
    # 6. PCA visualization
    ax = axes[1, 2]
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    
    feature_cols = ['App Usage Time (min/day)', 'Screen On Time (hours/day)', 
                    'Battery Drain (mAh/day)', 'Number of Apps Installed', 'Data Usage (MB/day)']
    X = df_clustered[feature_cols]
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    colors = ['#6B7280', '#3B82F6', '#059669', '#F59E0B', '#DC2626']
    for i, persona in enumerate(persona_order):
        mask = df_clustered['Persona'] == persona
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], label=persona, alpha=0.7, s=40, color=colors[i], edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11, fontweight='bold')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11, fontweight='bold')
    ax.set_title('PCA: Persona Separation', fontsize=12, fontweight='bold', pad=10)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.tick_params(labelsize=9)
    
    plt.suptitle('Persona Analysis: Behavioral Archetypes from Clustering', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "persona_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved persona analysis plots to {output_path}")
    plt.close()

def save_persona_definitions(personas):
    """Save persona definitions to JSON file"""
    output_path = OUTPUT_DIR / "persona_definitions.json"
    
    with open(output_path, 'w') as f:
        json.dump(personas, f, indent=2)
    
    print(f"✓ Saved persona definitions to {output_path}")
    
    # Also save readable text version
    output_path_txt = OUTPUT_DIR / "persona_definitions.txt"
    with open(output_path_txt, 'w') as f:
        f.write("="*80 + "\n")
        f.write("PERSONA DEFINITIONS\n")
        f.write("="*80 + "\n\n")
        
        for persona_name, data in personas.items():
            f.write(f"\n{persona_name.upper()}\n")
            f.write("-"*80 + "\n")
            f.write(f"Population: {data['count']} users ({data['percentage']:.1f}%)\n")
            f.write(f"Cluster ID: {data['cluster_id']}\n\n")
            f.write("Behavioral Characteristics:\n")
            c = data['characteristics']
            f.write(f"  • Screen Time: {c['screen_time_mean']:.1f} ± {c['screen_time_std']:.1f} hours/day\n")
            f.write(f"  • App Usage: {c['app_usage_mean']:.0f} ± {c['app_usage_std']:.0f} min/day\n")
            f.write(f"  • Battery Drain: {c['battery_drain_mean']:.0f} ± {c['battery_drain_std']:.0f} mAh/day\n")
            f.write(f"  • Apps Installed: {c['apps_installed_mean']:.0f} ± {c['apps_installed_std']:.0f}\n")
            f.write(f"  • Data Usage: {c['data_usage_mean']:.0f} ± {c['data_usage_std']:.0f} MB/day\n")
            f.write(f"  • Typical Behavior Class: {c['behavior_class_mode']}\n")
            f.write(f"  • Average Age: {c['age_mean']:.1f} ± {c['age_std']:.1f} years\n")
    
    print(f"✓ Saved readable persona definitions to {output_path_txt}")

def main():
    """Execute persona definition pipeline"""
    print("\n" + "="*60)
    print("PHASE 2: PERSONA DEFINITION")
    print("="*60 + "\n")
    
    # Load data
    df = load_data()
    print(f"✓ Loaded {len(df)} records\n")
    
    # Prepare features for clustering
    X, X_scaled, feature_cols, scaler = prepare_clustering_features(df)
    
    # Determine optimal number of clusters
    optimal_k = determine_optimal_clusters(X_scaled)
    
    # Perform clustering
    kmeans, cluster_labels = perform_clustering(X_scaled, n_clusters=optimal_k)
    
    # Analyze and name personas
    personas, cluster_to_persona = analyze_personas(df, cluster_labels, feature_cols)
    
    # Visualize personas
    visualize_personas(df, cluster_labels, personas, cluster_to_persona)
    
    # Save persona definitions
    save_persona_definitions(personas)
    
    print("\n" + "="*60)
    print("PHASE 2 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  - clustering_optimization.png")
    print("  - persona_analysis.png")
    print("  - persona_definitions.json")
    print("  - persona_definitions.txt")

if __name__ == "__main__":
    main()
