import React from 'react';

const Card = ({
    children,
    variant = 'default',
    className = '',
    ...props
}) => {
    const baseStyles = 'rounded-xl shadow-lg';

    const variantStyles = {
        default: 'bg-slate-900/90 border border-slate-700/60',
        glass: 'bg-slate-900/85 backdrop-blur-xl border border-slate-700/40',
        elevated: 'bg-slate-800/90 border border-slate-600/60 shadow-xl',
    };

    return (
        <div
            className={`${baseStyles} ${variantStyles[variant]} ${className} p-6`}
            {...props}
        >
            {children}
        </div>
    );
};

export default Card;