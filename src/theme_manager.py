"""
Theme Manager for the Cashbook Dashboard application.

This module provides centralized theme management, color schemes,
and styling utilities for consistent visual design across all components.
"""

import customtkinter as ctk
from typing import Dict, List, Tuple
import random


class ThemeManager:
    """
    Centralized theme management for consistent styling across the application.
    
    Provides color schemes, animation utilities, and styling constants
    for creating a cohesive visual experience.
    """
    
    # Color palette for cashbook differentiation
    CASHBOOK_COLORS = [
        "#3B82F6",  # Blue
        "#10B981",  # Emerald
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Violet
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
        "#EC4899",  # Pink
        "#6366F1",  # Indigo
        "#14B8A6",  # Teal
        "#A855F7",  # Purple
    ]
    
    # Dark theme color scheme
    DARK_THEME = {
        'primary': "#1F2937",      # Dark gray
        'secondary': "#374151",    # Medium gray
        'accent': "#3B82F6",       # Blue
        'success': "#10B981",      # Green
        'warning': "#F59E0B",      # Amber
        'error': "#EF4444",        # Red
        'surface': "#111827",      # Very dark gray
        'background': "#0F172A",   # Almost black
        'text_primary': "#F9FAFB", # Almost white
        'text_secondary': "#D1D5DB", # Light gray
        'text_muted': "#9CA3AF",   # Medium gray
        'border': "#374151",       # Medium gray
        'border_light': "#4B5563", # Lighter gray
        'hover': "#4B5563",        # Hover state
        'active': "#6B7280",       # Active state
    }
    
    # Animation settings
    ANIMATION = {
        'duration_fast': 150,      # Fast animations (ms)
        'duration_normal': 250,    # Normal animations (ms)
        'duration_slow': 400,      # Slow animations (ms)
        'easing': 'ease_out',      # Animation easing
    }
    
    # Typography settings
    TYPOGRAPHY = {
        'font_family': "Segoe UI",
        'sizes': {
            'xs': 10,
            'sm': 12,
            'base': 14,
            'lg': 16,
            'xl': 18,
            'xxl': 20,
            'title': 24,
            'heading': 28,
        },
        'weights': {
            'normal': 'normal',
            'medium': 'bold',
            'bold': 'bold',
        }
    }
    
    # Spacing system
    SPACING = {
        'xs': 4,
        'sm': 8,
        'base': 12,
        'md': 16,
        'lg': 20,
        'xl': 24,
        'xxl': 32,
        'xxxl': 40,
    }
    
    # Border radius system
    RADIUS = {
        'none': 0,
        'sm': 4,
        'base': 8,
        'md': 10,
        'lg': 12,
        'xl': 16,
        'full': 999,
    }
    
    @classmethod
    def get_cashbook_color(cls, cashbook_id: str) -> str:
        """
        Get a consistent color for a cashbook based on its ID.
        
        Args:
            cashbook_id: Unique identifier for the cashbook
            
        Returns:
            Hex color string
        """
        # Use hash of ID to get consistent color index
        color_index = hash(cashbook_id) % len(cls.CASHBOOK_COLORS)
        return cls.CASHBOOK_COLORS[color_index]
    
    @classmethod
    def get_random_cashbook_color(cls) -> str:
        """
        Get a random color from the cashbook color palette.
        
        Returns:
            Hex color string
        """
        return random.choice(cls.CASHBOOK_COLORS)
    
    @classmethod
    def create_font(cls, size: str = 'base', weight: str = 'normal') -> ctk.CTkFont:
        """
        Create a CTkFont with theme-consistent settings.
        
        Args:
            size: Font size key from TYPOGRAPHY['sizes']
            weight: Font weight key from TYPOGRAPHY['weights']
            
        Returns:
            CTkFont instance
        """
        font_size = cls.TYPOGRAPHY['sizes'].get(size, cls.TYPOGRAPHY['sizes']['base'])
        font_weight = cls.TYPOGRAPHY['weights'].get(weight, cls.TYPOGRAPHY['weights']['normal'])
        
        return ctk.CTkFont(
            family=cls.TYPOGRAPHY['font_family'],
            size=font_size,
            weight=font_weight
        )
    
    @classmethod
    def get_card_style(cls, variant: str = 'default') -> Dict:
        """
        Get styling configuration for cards.
        
        Args:
            variant: Card variant ('default', 'create', 'hover', 'active')
            
        Returns:
            Dictionary of styling properties
        """
        base_style = {
            'corner_radius': cls.RADIUS['md'],
            'border_width': 1,
            'width': 250,
            'height': 150,
        }
        
        if variant == 'default':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['surface'], cls.DARK_THEME['surface']),
                'border_color': (cls.DARK_THEME['border'], cls.DARK_THEME['border']),
            }
        elif variant == 'create':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['background'], cls.DARK_THEME['background']),
                'border_color': (cls.DARK_THEME['border_light'], cls.DARK_THEME['border_light']),
                'border_width': 2,
            }
        elif variant == 'hover':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['hover'], cls.DARK_THEME['hover']),
                'border_color': (cls.DARK_THEME['accent'], cls.DARK_THEME['accent']),
            }
        elif variant == 'active':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['active'], cls.DARK_THEME['active']),
                'border_color': (cls.DARK_THEME['accent'], cls.DARK_THEME['accent']),
            }
        
        return base_style
    
    @classmethod
    def get_button_style(cls, variant: str = 'primary') -> Dict:
        """
        Get styling configuration for buttons.
        
        Args:
            variant: Button variant ('primary', 'secondary', 'ghost', 'danger')
            
        Returns:
            Dictionary of styling properties
        """
        base_style = {
            'corner_radius': cls.RADIUS['base'],
            'font': cls.create_font('base', 'medium'),
            'height': 35,
        }
        
        if variant == 'primary':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['accent'], cls.DARK_THEME['accent']),
                'hover_color': ("#2563EB", "#2563EB"),  # Darker blue
                'text_color': (cls.DARK_THEME['text_primary'], cls.DARK_THEME['text_primary']),
            }
        elif variant == 'secondary':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['secondary'], cls.DARK_THEME['secondary']),
                'hover_color': (cls.DARK_THEME['hover'], cls.DARK_THEME['hover']),
                'text_color': (cls.DARK_THEME['text_primary'], cls.DARK_THEME['text_primary']),
            }
        elif variant == 'ghost':
            return {
                **base_style,
                'fg_color': 'transparent',
                'border_width': 1,
                'border_color': (cls.DARK_THEME['border'], cls.DARK_THEME['border']),
                'hover_color': (cls.DARK_THEME['hover'], cls.DARK_THEME['hover']),
                'text_color': (cls.DARK_THEME['text_secondary'], cls.DARK_THEME['text_secondary']),
            }
        elif variant == 'danger':
            return {
                **base_style,
                'fg_color': (cls.DARK_THEME['error'], cls.DARK_THEME['error']),
                'hover_color': ("#DC2626", "#DC2626"),  # Darker red
                'text_color': (cls.DARK_THEME['text_primary'], cls.DARK_THEME['text_primary']),
            }
        
        return base_style


class AnimationManager:
    """
    Manager for smooth animations and transitions.
    
    Provides utilities for creating smooth visual transitions
    and animations for interactive elements.
    """
    
    @staticmethod
    def animate_color_transition(
        widget, 
        target_color: str, 
        duration: int = 250,
        property_name: str = 'fg_color'
    ):
        """
        Animate a color transition on a widget.
        
        Args:
            widget: CTk widget to animate
            target_color: Target color (hex string)
            duration: Animation duration in milliseconds
            property_name: Widget property to animate ('fg_color', 'text_color', etc.)
        """
        # Note: CustomTkinter doesn't have built-in animation support
        # This is a placeholder for future animation implementation
        # For now, we'll use immediate color changes with hover effects
        try:
            widget.configure(**{property_name: target_color})
        except Exception:
            pass
    
    @staticmethod
    def animate_scale(widget, scale_factor: float = 1.05, duration: int = 150):
        """
        Animate a scale transformation on a widget.
        
        Args:
            widget: CTk widget to animate
            scale_factor: Scale multiplier (1.0 = no change, 1.1 = 10% larger)
            duration: Animation duration in milliseconds
        """
        # Note: CustomTkinter doesn't have built-in scale animations
        # This is a placeholder for future animation implementation
        # For now, we'll use visual feedback through color changes
        pass
    
    @staticmethod
    def animate_fade(widget, target_alpha: float = 1.0, duration: int = 300):
        """
        Animate opacity/fade transition on a widget.
        
        Args:
            widget: CTk widget to animate
            target_alpha: Target opacity (0.0 = transparent, 1.0 = opaque)
            duration: Animation duration in milliseconds
        """
        # Note: CustomTkinter doesn't have built-in fade animations
        # This is a placeholder for future animation implementation
        pass


class IconManager:
    """
    Manager for icons and visual indicators.
    
    Provides consistent icons and visual elements across the application.
    """
    
    # Unicode icons for different categories and states
    ICONS = {
        'cashbook': '📚',
        'create': '➕',
        'personal': '👤',
        'business': '💼',
        'travel': '✈️',
        'education': '🎓',
        'healthcare': '🏥',
        'entertainment': '🎬',
        'food': '🍽️',
        'shopping': '🛍️',
        'transport': '🚗',
        'home': '🏠',
        'other': '📁',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'settings': '⚙️',
        'delete': '🗑️',
        'edit': '✏️',
        'view': '👁️',
        'calendar': '📅',
        'money': '💰',
        'chart': '📊',
    }
    
    @classmethod
    def get_category_icon(cls, category: str) -> str:
        """
        Get an icon for a cashbook category.
        
        Args:
            category: Category name
            
        Returns:
            Unicode icon string
        """
        category_lower = category.lower()
        
        # Map common category names to icons
        category_mapping = {
            'personal': 'personal',
            'business': 'business',
            'work': 'business',
            'travel': 'travel',
            'vacation': 'travel',
            'education': 'education',
            'school': 'education',
            'healthcare': 'healthcare',
            'health': 'healthcare',
            'medical': 'healthcare',
            'entertainment': 'entertainment',
            'fun': 'entertainment',
            'food': 'food',
            'dining': 'food',
            'shopping': 'shopping',
            'transport': 'transport',
            'transportation': 'transport',
            'car': 'transport',
            'home': 'home',
            'house': 'home',
        }
        
        icon_key = category_mapping.get(category_lower, 'other')
        return cls.ICONS.get(icon_key, cls.ICONS['other'])
    
    @classmethod
    def get_status_icon(cls, status: str) -> str:
        """
        Get an icon for a status or state.
        
        Args:
            status: Status name ('success', 'warning', 'error', 'info')
            
        Returns:
            Unicode icon string
        """
        return cls.ICONS.get(status, cls.ICONS['info'])


# Global theme instance
theme = ThemeManager()
animations = AnimationManager()
icons = IconManager()