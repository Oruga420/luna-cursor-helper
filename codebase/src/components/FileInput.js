import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/solid';
import { Tooltip } from 'react-tooltip';

const FileInput = memo(({ 
  index, 
  value, 
  onChange, 
  onRemove, 
  error 
}) => {
  const inputId = `file-path-${index}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className="mt-1 flex rounded-md shadow-sm"
    >
      <div className="relative flex-grow">
        <input
          type="text"
          id={inputId}
          className={`flex-1 block w-full rounded-md sm:text-sm ${
            error
              ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
          }`}
          value={value}
          onChange={(e) => onChange(index, e.target.value)}
          placeholder="Enter file path"
          data-tooltip-id={`file-path-tooltip-${index}`}
          data-tooltip-content="Enter the full path to your file"
        />
        {error && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg
              className="h-5 w-5 text-red-500"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        )}
      </div>
      {index > 0 && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          type="button"
          onClick={() => onRemove(index)}
          className="ml-2 inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          aria-label="Remove file path"
        >
          <XMarkIcon className="h-4 w-4" />
        </motion.button>
      )}
      <Tooltip id={`file-path-tooltip-${index}`} place="top" />
      {error && (
        <div className="mt-1 text-sm text-red-600">{error}</div>
      )}
    </motion.div>
  );
});

FileInput.displayName = 'FileInput';

export default FileInput; 