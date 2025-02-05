import React from 'react';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const spinTransition = {
    repeat: Infinity,
    duration: 1,
    ease: "linear"
  };

  return (
    <div className="flex justify-center items-center">
      <motion.div
        className={`${sizes[size]} border-4 border-indigo-200 border-t-indigo-600 rounded-full`}
        animate={{ rotate: 360 }}
        transition={spinTransition}
      />
    </div>
  );
};

export default LoadingSpinner; 