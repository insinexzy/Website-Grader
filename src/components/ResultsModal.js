import React from 'react';

const ResultsModal = ({ results, onClose }) => {
  if (!results) return null;

  console.log('Rendering ResultsModal with results:', results);

  // Extract the actual results from the response structure
  const analysisResults = results.results || results;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getProgressBarColor = (score) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  const formatScore = (score) => {
    return typeof score === 'number' ? Math.round(score) : score;
  };

  // Helper function to render category details
  const renderCategoryDetails = (category, data) => {
    return (
      <div key={category} className="p-4 bg-white border rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="font-medium capitalize">{category.replace(/_/g, ' ')}</span>
          {data.score !== undefined && (
            <div className="flex items-center">
              <span className={`${getScoreColor(data.score)} font-semibold`}>
                {formatScore(data.score)}
              </span>
              {data.max_score && (
                <span className="text-gray-400 text-sm ml-1">/ {data.max_score}</span>
              )}
            </div>
          )}
        </div>

        {data.score !== undefined && (
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              className={`${getProgressBarColor(data.score)} h-2 rounded-full`}
              style={{ width: `${(data.score / (data.max_score || 100)) * 100}%` }}
            ></div>
          </div>
        )}
        
        {data.strengths && data.strengths.length > 0 && (
          <div className="mt-3">
            <h5 className="text-sm font-medium text-green-600 mb-1">Strengths</h5>
            <ul className="list-disc list-inside space-y-1">
              {data.strengths.map((item, index) => (
                <li key={index} className="text-sm text-gray-600">{item}</li>
              ))}
            </ul>
          </div>
        )}

        {data.issues && data.issues.length > 0 && (
          <div className="mt-3">
            <h5 className="text-sm font-medium text-red-600 mb-1">Issues</h5>
            <ul className="list-disc list-inside space-y-1">
              {data.issues.map((item, index) => (
                <li key={index} className="text-sm text-gray-600">{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Display any other properties that aren't already shown */}
        {Object.entries(data).map(([key, value]) => {
          if (!['score', 'max_score', 'strengths', 'issues'].includes(key) && typeof value !== 'object') {
            return (
              <div key={key} className="mt-2">
                <span className="font-medium capitalize">{key.replace(/_/g, ' ')}: </span>
                <span className="text-gray-600">{value}</span>
              </div>
            );
          }
          return null;
        })}
      </div>
    );
  };

  // Get categories and their data
  const categoryData = Object.entries(analysisResults).reduce((acc, [key, value]) => {
    if (
      typeof value === 'object' && 
      value !== null && 
      !['lead_quality_score'].includes(key) &&
      key !== 'results'
    ) {
      acc[key] = value;
    }
    return acc;
  }, {});

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start sticky top-0 bg-white pb-4 z-10">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <p className="mt-1 text-sm text-gray-500">{results.url}</p>
            </div>
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

          {/* Overall Score */}
          <div className="mt-6 p-6 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-900">Overall Score</h3>
              <div className={`${getScoreBgColor(analysisResults.total_score)} px-4 py-2 rounded-full`}>
                <span className={`text-2xl font-bold ${getScoreColor(analysisResults.total_score)}`}>
                  {formatScore(analysisResults.total_score)}
                </span>
              </div>
            </div>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`${getProgressBarColor(analysisResults.total_score)} h-2.5 rounded-full`}
                style={{ width: `${analysisResults.total_score}%` }}
              ></div>
            </div>
          </div>

          {/* Classification and Lead Potential */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white border rounded-lg">
              <h4 className="font-medium text-gray-900">Classification</h4>
              <p className="mt-1 text-gray-600">{analysisResults.classification || 'Not classified'}</p>
            </div>
            <div className="p-4 bg-white border rounded-lg">
              <h4 className="font-medium text-gray-900">Lead Potential</h4>
              <p className="mt-1 text-gray-600">{analysisResults.lead_potential || 'Not evaluated'}</p>
            </div>
          </div>

          {/* Category Details */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Analysis</h3>
            <div className="space-y-4">
              {Object.entries(categoryData).map(([category, data]) => 
                renderCategoryDetails(category, data)
              )}
            </div>
          </div>

          {/* Lead Quality Assessment */}
          {analysisResults.lead_quality_score && (
            <div className="mt-6 p-6 bg-white border rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Quality Assessment</h3>
              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="font-medium">Priority:</span>
                  <span className="ml-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800">
                    {analysisResults.lead_quality_score.priority}
                  </span>
                </div>
                <p className="text-gray-600">{analysisResults.lead_quality_score.reason}</p>
                <p className="text-gray-600">{analysisResults.lead_quality_score.estimated_work}</p>
              </div>
            </div>
          )}

          {/* Additional Information */}
          <div className="mt-6 text-sm text-gray-500">
            <p>Analysis completed at: {analysisResults.timestamp || results.timestamp}</p>
            <p>Response time: {((analysisResults.load_time || results.load_time || 0) * 1000).toFixed(2)}ms</p>
            {analysisResults.status_code && (
              <p>Status code: {analysisResults.status_code}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsModal; 