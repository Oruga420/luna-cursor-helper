import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const CustomTooltip = ({ 
  content, 
  isVisible, 
  position = { x: 0, y: 0 } 
}) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 5 }}
          transition={{ duration: 0.2 }}
          className="absolute z-50 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg shadow-sm"
          style={{
            left: position.x,
            top: position.y
          }}
        >
          {content}
          <div
            className="absolute w-2 h-2 bg-gray-900 transform rotate-45"
            style={{
              top: '-0.25rem',
              left: '50%',
              marginLeft: '-0.25rem'
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CustomTooltip; 