import React from 'react';

const ResultsModal = ({ results, onClose }) => {
  if (!results) return null;

  const getScoreColor = (score) => {
    if (score < 30) return 'text-red-800';
    if (score < 50) return 'text-yellow-600';
    if (score < 70) return 'text-green-500';
    return 'text-green-700';
  };

  const getScoreBgColor = (score) => {
    if (score < 30) return 'bg-red-100';
    if (score < 50) return 'bg-yellow-100';
    if (score < 70) return 'bg-green-100';
    return 'bg-green-200';
  };

  const getProgressBarColor = (score) => {
    if (score < 30) return 'bg-red-600';
    if (score < 50) return 'bg-yellow-500';
    if (score < 70) return 'bg-green-500';
    return 'bg-green-700';
  };

  const formatScore = (score) => {
    return typeof score === 'number' ? Math.round(score) : score;
  };

  const categoryLabels = {
    ssl: 'SSL Certificate',
    mobile: 'Mobile-Friendliness',
    page_speed: 'Page Speed',
    tech_stack: 'Technology Stack',
    ui_quality: 'UI Quality',
    seo: 'SEO Optimization',
    security: 'Security Headers',
    accessibility: 'Accessibility',
    content: 'Content Quality'
  };

  // Extract the actual results from the response structure
  const analysisResults = results.results || results;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <p className="mt-1 text-sm text-gray-500">{analysisResults.url}</p>
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
          <div className={`${getScoreBgColor(analysisResults.total_score)} rounded-lg p-6 mb-6`}>
            <div className="flex justify-between items-center">
              <div>
              <h3 className="text-xl font-semibold text-gray-900">Overall Score</h3>
                <p className="mt-1 text-sm text-gray-600">{analysisResults.classification}</p>
              </div>
              <div className={`text-4xl font-bold ${getScoreColor(analysisResults.total_score)}`}>
                  {formatScore(analysisResults.total_score)}
              </div>
            </div>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`${getProgressBarColor(analysisResults.total_score)} h-2.5 rounded-full transition-all duration-500`}
                style={{ width: `${analysisResults.total_score}%` }}
              ></div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="text-sm font-medium text-gray-500">Lead Potential</h4>
              <p className="mt-1 text-lg font-semibold">{analysisResults.lead_potential}</p>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="text-sm font-medium text-gray-500">Load Time</h4>
              <p className="mt-1 text-lg font-semibold">{analysisResults.load_time.toFixed(2)}s</p>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="text-sm font-medium text-gray-500">Status</h4>
              <p className="mt-1 text-lg font-semibold">{analysisResults.status_code}</p>
            </div>
          </div>

          {/* Category Scores */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Category Scores</h3>
            {Object.entries(categoryLabels).map(([key, label]) => {
              const categoryData = analysisResults.categories[key];
              if (!categoryData) return null;

              const score = categoryData.score;
              const maxScore = categoryData.max_score;
              const percentage = (score / maxScore) * 100;

              return (
                <div key={key} className="bg-white rounded-lg border p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium text-gray-900">{label}</h4>
                    <div className={`${getScoreColor(percentage)} font-semibold`}>
                      {score}/{maxScore}
            </div>
          </div>

                  <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div
                      className={`${getProgressBarColor(percentage)} h-2 rounded-full transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                </div>

                  {/* Details */}
                  {categoryData.details && categoryData.details.length > 0 && (
                    <div className="mt-3">
                      <h5 className="text-sm font-medium text-green-600 mb-1">Details</h5>
                      <ul className="list-disc list-inside space-y-1">
                        {categoryData.details.map((detail, index) => (
                          <li key={index} className="text-sm text-gray-600">{detail}</li>
                        ))}
                      </ul>
            </div>
          )}

                  {/* Issues */}
                  {categoryData.issues && categoryData.issues.length > 0 && (
                    <div className="mt-3">
                      <h5 className="text-sm font-medium text-red-600 mb-1">Issues</h5>
                      <ul className="list-disc list-inside space-y-1">
                        {categoryData.issues.map((issue, index) => (
                          <li key={index} className="text-sm text-gray-600">{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Analysis Info */}
          <div className="mt-6 text-sm text-gray-500">
            <p>Analysis completed at: {analysisResults.timestamp}</p>
            <p>Response time: {(analysisResults.load_time * 1000).toFixed(2)}ms</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsModal; 