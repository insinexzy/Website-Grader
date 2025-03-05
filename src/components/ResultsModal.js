import React from 'react';

const ResultsModal = ({ results, onClose }) => {
  if (!results) return null;

  console.log('Rendering ResultsModal with results:', results);

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start">
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="mt-6 space-y-6">
            {Object.entries(results).map(([category, value]) => (
              <div key={category} className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-medium text-gray-900 capitalize">
                  {category.replace(/_/g, ' ')}
                </h3>
                <div className="mt-2 text-sm text-gray-500">
                  {typeof value === 'object' ? (
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  ) : (
                    <p>{String(value)}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsModal; 