import React from 'react';

const PageHeader = ({ title, description, icon }) => {
    return (
        <div className="mb-6">
            <div className="flex items-center space-x-4 mb-2">
                {icon && (
                    <div className="p-3 bg-gradient-to-br from-blue-600/20 to-violet-600/20 rounded-xl border border-blue-500/30">
                        {icon}
                    </div>
                )}
                <h1 className="text-3xl font-bold text-white">{title}</h1>
            </div>
            {description && (
                <p className="text-slate-300 mt-2 max-w-3xl">{description}</p>
            )}
        </div>
    );
};

export default PageHeader;