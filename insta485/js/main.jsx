import React from 'react';
import ReactDOM from 'react-dom';
import Batch from './middle';

// This method is only called once
// {/* <Post url="/api/v1/posts/1/" />, */}
ReactDOM.render(
  // Insert the post component into the DOM
  <Batch url="/api/v1/posts/?size=10" />,
  document.getElementById('reactEntry'),
);
