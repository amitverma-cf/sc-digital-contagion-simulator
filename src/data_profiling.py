"""
Phase 1: Dataset Intake & Profiling
Analyzes user_behavior_dataset.csv to extract statistical properties
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration
DATA_PATH = Path(__file__).parent.parent / "user_behavior_dataset.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_and_verify_dataset():
    """Load dataset and verify integrity"""
    print("="*60)
    print("DATASET VERIFICATION")
    print("="*60)
    
    df = pd.read_csv(DATA_PATH)
    
    print(f"\n✓ Loaded {len(df)} rows")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✓ No missing values detected")
    else:
        print(f"⚠ Missing values found:\n{missing[missing > 0]}")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"✓ Duplicate rows: {duplicates}")
    
    return df

def profile_numerical_columns(df):
    """Generate statistics for numerical columns"""
    print("\n" + "="*60)
    print("NUMERICAL COLUMN PROFILING")
    print("="*60)
    
    numerical_cols = [
        'App Usage Time (min/day)',
        'Screen On Time (hours/day)',
        'Battery Drain (mAh/day)',
        'Number of Apps Installed',
        'Data Usage (MB/day)',
        'Age'
    ]
    
    stats = {}
    for col in numerical_cols:
        if col in df.columns:
            data = df[col]
            stats[col] = {
                'mean': data.mean(),
                'std': data.std(),
                'min': data.min(),
                'q25': data.quantile(0.25),
                'median': data.median(),
                'q75': data.quantile(0.75),
                'max': data.max(),
                'skewness': data.skew(),
                'kurtosis': data.kurtosis()
            }
            
            print(f"\n{col}:")
            print(f"  Mean: {stats[col]['mean']:.2f} ± {stats[col]['std']:.2f}")
            print(f"  Range: [{stats[col]['min']:.2f}, {stats[col]['max']:.2f}]")
            print(f"  Quartiles: Q1={stats[col]['q25']:.2f}, Q2={stats[col]['median']:.2f}, Q3={stats[col]['q75']:.2f}")
            print(f"  Skewness: {stats[col]['skewness']:.2f}, Kurtosis: {stats[col]['kurtosis']:.2f}")
    
    return stats

def profile_categorical_columns(df):
    """Generate statistics for categorical columns"""
    print("\n" + "="*60)
    print("CATEGORICAL COLUMN PROFILING")
    print("="*60)
    
    categorical_cols = ['Device Model', 'Operating System', 'Gender', 'User Behavior Class']
    
    for col in categorical_cols:
        if col in df.columns:
            print(f"\n{col}:")
            value_counts = df[col].value_counts()
            for value, count in value_counts.items():
                pct = (count / len(df)) * 100
                print(f"  {value}: {count} ({pct:.1f}%)")
    
    return

def detect_outliers(df):
    """Detect outliers using IQR method"""
    print("\n" + "="*60)
    print("OUTLIER DETECTION (IQR Method)")
    print("="*60)
    
    numerical_cols = [
        'App Usage Time (min/day)',
        'Screen On Time (hours/day)',
        'Battery Drain (mAh/day)',
        'Number of Apps Installed',
        'Data Usage (MB/day)',
        'Age'
    ]
    
    outliers_report = {}
    for col in numerical_cols:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outliers_report[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(df)) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
            
            if len(outliers) > 0:
                print(f"\n{col}:")
                print(f"  Outliers: {len(outliers)} ({outliers_report[col]['percentage']:.1f}%)")
                print(f"  Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")
            else:
                print(f"\n{col}: No outliers detected")
    
    return outliers_report

def visualize_distributions(df):
    """Create distribution plots for key variables"""
    print("\n" + "="*60)
    print("GENERATING DISTRIBUTION VISUALIZATIONS")
    print("="*60)
    
    numerical_cols = [
        'App Usage Time (min/day)',
        'Screen On Time (hours/day)',
        'Battery Drain (mAh/day)',
        'User Behavior Class'
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colors = ['#3B82F6', '#059669', '#F59E0B', '#DC2626']
    
    for idx, col in enumerate(numerical_cols):
        if col in df.columns:
            axes[idx].hist(df[col], bins=30, edgecolor='black', alpha=0.8, color=colors[idx], linewidth=1.5)
            axes[idx].set_xlabel(col, fontsize=12, fontweight='bold')
            axes[idx].set_ylabel('Frequency', fontsize=12, fontweight='bold')
            axes[idx].set_title(f'Distribution of {col}', fontsize=13, fontweight='bold', pad=10)
            axes[idx].grid(True, alpha=0.4, linestyle='--')
            axes[idx].tick_params(labelsize=10)
            
            # Add mean line
            mean_val = df[col].mean()
            axes[idx].axvline(mean_val, color='#EF4444', linestyle='--', linewidth=3, label=f'Mean: {mean_val:.1f}')
            axes[idx].legend(fontsize=10, framealpha=0.95)
    
    plt.suptitle('Data Distributions: Key Behavioral Metrics', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "distribution_plots.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved distribution plots to {output_path}")
    plt.close()
    
    # Correlation heatmap
    numerical_data = df.select_dtypes(include=[np.number])
    plt.figure(figsize=(10, 8))
    correlation_matrix = numerical_data.corr()
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 9})
    plt.title('Correlation Matrix: Feature Relationships', fontsize=12, fontweight='bold', pad=10)
    plt.xticks(fontsize=10, rotation=45, ha='right')
    plt.yticks(fontsize=10)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "correlation_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved correlation heatmap to {output_path}")
    plt.close()

def save_profiling_report(df, stats, outliers_report):
    """Save comprehensive profiling report"""
    output_path = OUTPUT_DIR / "profiling_report.txt"
    
    with open(output_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("DATASET PROFILING REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Dataset: user_behavior_dataset.csv\n")
        f.write(f"Total Records: {len(df)}\n")
        f.write(f"Total Features: {len(df.columns)}\n\n")
        
        f.write("NUMERICAL STATISTICS\n")
        f.write("-"*80 + "\n")
        for col, stat in stats.items():
            f.write(f"\n{col}:\n")
            f.write(f"  Mean ± Std: {stat['mean']:.2f} ± {stat['std']:.2f}\n")
            f.write(f"  Min/Max: {stat['min']:.2f} / {stat['max']:.2f}\n")
            f.write(f"  Quartiles: Q1={stat['q25']:.2f}, Q2={stat['median']:.2f}, Q3={stat['q75']:.2f}\n")
        
        f.write("\n\nOUTLIER SUMMARY\n")
        f.write("-"*80 + "\n")
        for col, outlier in outliers_report.items():
            if outlier['count'] > 0:
                f.write(f"{col}: {outlier['count']} outliers ({outlier['percentage']:.1f}%)\n")
        
        f.write("\n\nDECISION: Keep all data points (outliers represent valid extreme behaviors)\n")
    
    print(f"✓ Saved profiling report to {output_path}")

def main():
    """Execute complete profiling pipeline"""
    print("\n" + "="*60)
    print("PHASE 1: DATASET INTAKE & PROFILING")
    print("="*60 + "\n")
    
    # Load and verify
    df = load_and_verify_dataset()
    
    # Profile numerical columns
    stats = profile_numerical_columns(df)
    
    # Profile categorical columns
    profile_categorical_columns(df)
    
    # Detect outliers
    outliers_report = detect_outliers(df)
    
    # Generate visualizations
    visualize_distributions(df)
    
    # Save report
    save_profiling_report(df, stats, outliers_report)
    
    print("\n" + "="*60)
    print("PHASE 1 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  - distribution_plots.png")
    print("  - correlation_heatmap.png")
    print("  - profiling_report.txt")

if __name__ == "__main__":
    main()
