import React from 'react';

function LoadingSpinner() {
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl flex flex-col items-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-indigo-600"></div>
        <p className="mt-4 text-lg font-semibold text-gray-700">Analyzing Website...</p>
        <p className="mt-2 text-sm text-gray-500">This may take a few moments</p>
      </div>
    </div>
  );
}

export default LoadingSpinner; 