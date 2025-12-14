# data_preprocessor.py
# Generic Data Preprocessing Class - Reusable for any dataset

import pandas as pd
import numpy as np
from typing import Union, List, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """
    Generic data preprocessing class for handling missing values and feature engineering.
    Can be reused for any dataset.
    
    Example:
        >>> from data_preprocessor import DataPreprocessor
        >>> df = pd.read_csv('data.csv')
        >>> prep = DataPreprocessor(df)
        >>> prep.add_binary_flag('column_name').fill_median('numeric_col')
        >>> prep.save_processed_data('processed.csv')
    """
    
    def __init__(self, df: pd.DataFrame, verbose: bool = True):
        """
        Initialize with dataframe
        
        Args:
            df: Input dataframe
            verbose: Print processing steps
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.processing_log = []
        self.verbose = verbose
        self.new_features = []
        
    def _log(self, message: str) -> None:
        """Internal logging method"""
        self.processing_log.append(message)
        if self.verbose:
            print(f"✅ {message}")
    
    def add_binary_flag(self, column: str, flag_name: Optional[str] = None) -> 'DataPreprocessor':
        """
        Add binary flag indicating if original value was missing
        
        Args:
            column: Column name to create flag for
            flag_name: Name for the flag column (default: has_{column})
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        if flag_name is None:
            flag_name = f'has_{column.lower().replace(" ", "_").replace("-", "_")}'
        
        self.df[flag_name] = self.df[column].notna().astype(int)
        self.new_features.append(flag_name)
        self._log(f"Created binary flag '{flag_name}' for '{column}'")
        return self
    
    def fill_value(self, column: str, value: Union[str, int, float]) -> 'DataPreprocessor':
        """
        Fill missing values with a specific value
        
        Args:
            column: Column name to fill
            value: Value to fill with
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        if missing_count > 0:
            self.df[column].fillna(value, inplace=True)
            self._log(f"Filled {missing_count:,} missing values in '{column}' with '{value}'")
        return self
    
    def fill_median(self, column: str, group_by: Optional[str] = None) -> 'DataPreprocessor':
        """
        Fill missing values with median (optionally grouped)
        
        Args:
            column: Column name to fill
            group_by: Column to group by for median calculation
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        
        if missing_count == 0:
            return self
        
        if group_by and group_by in self.df.columns:
            self.df[column] = self.df.groupby(group_by)[column].transform(
                lambda x: x.fillna(x.median() if not x.dropna().empty else self.df[column].median())
            )
            self._log(f"Filled {missing_count:,} missing values in '{column}' with grouped median by '{group_by}'")
        else:
            median_value = self.df[column].median()
            self.df[column].fillna(median_value, inplace=True)
            self._log(f"Filled {missing_count:,} missing values in '{column}' with median ({median_value:.2f})")
        return self
    
    def fill_mode(self, column: str, group_by: Optional[str] = None) -> 'DataPreprocessor':
        """
        Fill missing values with mode (most frequent value)
        
        Args:
            column: Column name to fill
            group_by: Column to group by for mode calculation
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        
        if missing_count == 0:
            return self
            
        if group_by and group_by in self.df.columns:
            self.df[column] = self.df.groupby(group_by)[column].transform(
                lambda x: x.fillna(x.mode()[0] if not x.dropna().empty and len(x.mode()) > 0 else self.df[column].mode()[0])
            )
            self._log(f"Filled {missing_count:,} missing values in '{column}' with grouped mode by '{group_by}'")
        else:
            if not self.df[column].dropna().empty:
                mode_value = self.df[column].mode()[0]
                self.df[column].fillna(mode_value, inplace=True)
                self._log(f"Filled {missing_count:,} missing values in '{column}' with mode ({mode_value})")
        return self
    
    def fill_mean(self, column: str, group_by: Optional[str] = None) -> 'DataPreprocessor':
        """
        Fill missing values with mean
        
        Args:
            column: Column name to fill
            group_by: Column to group by for mean calculation
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        
        if missing_count == 0:
            return self
            
        if group_by and group_by in self.df.columns:
            self.df[column] = self.df.groupby(group_by)[column].transform(
                lambda x: x.fillna(x.mean() if not x.dropna().empty else self.df[column].mean())
            )
            self._log(f"Filled {missing_count:,} missing values in '{column}' with grouped mean by '{group_by}'")
        else:
            mean_value = self.df[column].mean()
            self.df[column].fillna(mean_value, inplace=True)
            self._log(f"Filled {missing_count:,} missing values in '{column}' with mean ({mean_value:.2f})")
        return self
    
    def fill_forward(self, column: str) -> 'DataPreprocessor':
        """
        Forward fill missing values
        
        Args:
            column: Column name to fill
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        if missing_count > 0:
            self.df[column].fillna(method='ffill', inplace=True)
            self._log(f"Forward filled {missing_count:,} missing values in '{column}'")
        return self
    
    def fill_backward(self, column: str) -> 'DataPreprocessor':
        """
        Backward fill missing values
        
        Args:
            column: Column name to fill
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        if missing_count > 0:
            self.df[column].fillna(method='bfill', inplace=True)
            self._log(f"Backward filled {missing_count:,} missing values in '{column}'")
        return self
    
    def fill_interpolate(self, column: str, method: str = 'linear') -> 'DataPreprocessor':
        """
        Interpolate missing values
        
        Args:
            column: Column name to fill
            method: Interpolation method ('linear', 'polynomial', 'spline')
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        missing_count = self.df[column].isna().sum()
        if missing_count > 0:
            self.df[column].interpolate(method=method, inplace=True)
            self._log(f"Interpolated {missing_count:,} missing values in '{column}' using {method} method")
        return self
    
    def create_feature(self, feature_name: str, formula: callable, 
                      description: Optional[str] = None) -> 'DataPreprocessor':
        """
        Create new feature using custom formula
        
        Args:
            feature_name: Name for new feature
            formula: Lambda function to calculate feature
            description: Optional description of the feature
        
        Returns:
            self for method chaining
        """
        try:
            self.df[feature_name] = formula(self.df)
            self.new_features.append(feature_name)
            desc = description or feature_name
            self._log(f"Created new feature: {desc} ('{feature_name}')")
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Error creating feature '{feature_name}': {str(e)}")
        return self
    
    def cap_outliers(self, column: str, lower_percentile: float = 1, 
                    upper_percentile: float = 99) -> 'DataPreprocessor':
        """
        Cap outliers at specified percentiles
        
        Args:
            column: Column name to cap
            lower_percentile: Lower percentile for capping
            upper_percentile: Upper percentile for capping
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        lower_bound = self.df[column].quantile(lower_percentile / 100)
        upper_bound = self.df[column].quantile(upper_percentile / 100)
        
        original_outliers = ((self.df[column] < lower_bound) | (self.df[column] > upper_bound)).sum()
        
        if original_outliers > 0:
            self.df[column] = self.df[column].clip(lower_bound, upper_bound)
            self._log(f"Capped {original_outliers:,} outliers in '{column}' at {lower_percentile}-{upper_percentile} percentile")
        return self
    
    def cap_outliers_iqr(self, column: str, multiplier: float = 1.5) -> 'DataPreprocessor':
        """
        Cap outliers using IQR method
        
        Args:
            column: Column name to cap
            multiplier: IQR multiplier (default 1.5)
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
            
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        original_outliers = ((self.df[column] < lower_bound) | (self.df[column] > upper_bound)).sum()
        
        if original_outliers > 0:
            self.df[column] = self.df[column].clip(lower_bound, upper_bound)
            self._log(f"Capped {original_outliers:,} outliers in '{column}' using IQR method")
        return self
    
    def extract_from_address(self, address_column: str = 'Address', 
                             patterns: Optional[Dict[str, str]] = None) -> 'DataPreprocessor':
        """
        Extract 'City', 'District', and 'StreetAndWard' features from address column using comma splitting.
        
        Args:
            address_column: Name of address column
            patterns: Dictionary of regex patterns (Not used in this split logic, kept for compatibility)
        
        Returns:
            self for method chaining
        """
        if address_column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{address_column}' not found")
            return self
        
        # Helper function to parse address
        def _parse_location(addr):
            if not isinstance(addr, str) or not addr:
                return 'Unknown', 'Unknown', 'Unknown'
            
            # Split by comma and strip whitespace
            parts = [p.strip() for p in addr.split(',')]
            
            city = 'Unknown'
            district = 'Unknown'
            street_ward = 'Unknown'
            
            # Logic based on number of parts
            if len(parts) >= 3:
                city = parts[-1].rstrip('.')          # Last part is City
                district = parts[-2]                  # Second last is District
                street_ward = ", ".join(parts[:-2])   # The rest is Street + Ward
                
            elif len(parts) == 2:
                city = parts[-1].rstrip('.')
                district = parts[-2]
                street_ward = 'Unknown'               # Not enough details
                
            elif len(parts) == 1:
                city = parts[0].rstrip('.')
                
            return city, district, street_ward
            
        # Apply parsing logic and unzip into 3 lists
        cities, districts, street_wards = zip(*self.df[address_column].apply(_parse_location))
        
        # Assign new columns
        self.df['new_city'] = cities
        self.df['new_district'] = districts
        self.df['new_street_ward'] = street_wards
        
        # Update new features list
        for feature in ['new_city', 'new_district', 'new_street_ward']:
            self.df[feature] = self.df[feature].fillna('Unknown')
            if feature not in self.new_features:
                self.new_features.append(feature)
            
        self._log(f"Extracted 'new_city', 'new_district', 'new_street_ward' from '{address_column}'")
        return self
        
    def create_bins(self, column: str, n_bins: int = 5, 
                   labels: Optional[List[str]] = None) -> 'DataPreprocessor':
        """
        Create bins for continuous variables
        
        Args:
            column: Column name to bin
            n_bins: Number of bins
            labels: Labels for bins
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
        
        new_col = f'{column}_binned'
        try:
            self.df[new_col] = pd.cut(self.df[column], bins=n_bins, labels=labels)
            self.new_features.append(new_col)
            self._log(f"Created {n_bins} bins for '{column}'")
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Error binning '{column}': {str(e)}")
        return self
    
    def scale_feature(self, column: str, method: str = 'standard') -> 'DataPreprocessor':
        """
        Scale numerical features
        
        Args:
            column: Column name to scale
            method: Scaling method ('standard', 'minmax', 'robust')
        
        Returns:
            self for method chaining
        """
        if column not in self.df.columns:
            if self.verbose:
                print(f"⚠️ Column '{column}' not found")
            return self
        
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
        
        scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        
        if method in scalers:
            scaler = scalers[method]
            new_col = f'{column}_scaled'
            self.df[new_col] = scaler.fit_transform(self.df[[column]])
            self.new_features.append(new_col)
            self._log(f"Scaled '{column}' using {method} method")
        return self
    
    def get_missing_summary(self) -> pd.DataFrame:
        """
        Get summary of missing values
        
        Returns:
            DataFrame with missing value statistics
        """
        missing_df = pd.DataFrame({
            'Column': self.df.columns,
            'Missing_Count': self.df.isnull().sum(),
            'Missing_Percentage': (self.df.isnull().sum() / len(self.df) * 100).round(2)
        })
        return missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Percentage', ascending=False)
    
    def get_numeric_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for numeric columns
        
        Returns:
            DataFrame with numeric column statistics
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            return self.df[numeric_cols].describe()
        else:
            return pd.DataFrame()
    
    def get_categorical_summary(self) -> Dict[str, pd.Series]:
        """
        Get summary for categorical columns
        
        Returns:
            Dictionary with value counts for each categorical column
        """
        cat_cols = self.df.select_dtypes(include=['object']).columns
        summary = {}
        for col in cat_cols:
            summary[col] = self.df[col].value_counts().head(10)
        return summary
    
    def save_processed_data(self, filename: str = 'processed_data.csv', 
                          index: bool = False) -> None:
        """
        Save processed dataframe to CSV
        
        Args:
            filename: Output filename
            index: Whether to save index
        """
        self.df.to_csv(filename, index=index,encoding='utf-8-sig')
        if self.verbose:
            print(f"\n💾 Saved processed data to '{filename}'")
            print(f"   Shape: {self.df.shape}")
            print(f"   Original features: {len(self.original_df.columns)}")
            print(f"   New features added: {len(self.new_features)}")
            print(f"   Total features: {len(self.df.columns)}")
    
    def save_processing_log(self, filename: str = 'processing_log.txt') -> None:
        """
        Save processing log to text file
        
        Args:
            filename: Log filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DATA PREPROCESSING LOG\n")
            f.write("="*50 + "\n\n")
            for i, log in enumerate(self.processing_log, 1):
                f.write(f"{i}. {log}\n")
        if self.verbose:
            print(f"📝 Saved processing log to '{filename}'")
    
    def print_processing_summary(self) -> None:
        """
        Print summary of all processing steps
        """
        print("\n" + "="*80)
        print("📋 PROCESSING SUMMARY")
        print("="*80)
        
        print(f"\n📊 Data Shape:")
        print(f"   Original: {self.original_df.shape}")
        print(f"   Current: {self.df.shape}")
        
        print(f"\n🔧 Processing Steps ({len(self.processing_log)}):")
        for i, log in enumerate(self.processing_log[-10:], 1):  # Show last 10 steps
            print(f"   {i}. {log}")
        
        if len(self.processing_log) > 10:
            print(f"   ... and {len(self.processing_log)-10} more steps")
        
        print(f"\n✨ New Features Created ({len(self.new_features)}):")
        if self.new_features:
            for feature in self.new_features[:10]:  # Show first 10
                print(f"   • {feature}")
            if len(self.new_features) > 10:
                print(f"   ... and {len(self.new_features)-10} more features")
        
        print("\n📊 Missing Values Status:")
        missing_summary = self.get_missing_summary()
        if len(missing_summary) > 0:
            print(missing_summary.to_string(index=False))
        else:
            print("   ✅ No missing values remaining!")
    
    def reset(self) -> 'DataPreprocessor':
        """
        Reset to original dataframe
        
        Returns:
            self for method chaining
        """
        self.df = self.original_df.copy()
        self.processing_log = []
        self.new_features = []
        if self.verbose:
            print("🔄 Reset to original dataframe")
        return self