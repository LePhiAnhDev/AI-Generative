import React from 'react';

const Button = ({
    children,
    onClick,
    variant = 'primary',
    size = 'md',
    className = '',
    disabled = false,
    ...props
}) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantStyles = {
        primary: 'bg-gradient-to-r from-blue-700 to-violet-700 text-white hover:from-blue-600 hover:to-violet-600 focus:ring-blue-500 shadow-lg hover:shadow-xl transform hover:scale-105 border border-blue-600/20',
        secondary: 'bg-slate-900/90 border border-slate-700/60 text-slate-200 hover:bg-slate-800/90 focus:ring-slate-500',
        success: 'bg-emerald-600 border border-emerald-600/60 text-white hover:bg-emerald-500 focus:ring-emerald-500',
        danger: 'bg-red-600 border border-red-600/60 text-white hover:bg-red-500 focus:ring-red-500',
        ghost: 'bg-transparent text-slate-200 hover:bg-slate-800/60 focus:ring-slate-500 border border-transparent',
    };

    const sizeStyles = {
        sm: 'text-sm px-3 py-1.5 h-8',
        md: 'text-sm px-4 py-2 h-10',
        lg: 'text-base px-6 py-2.5 h-12',
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;