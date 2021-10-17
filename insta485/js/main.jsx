import React from 'react';
import ReactDOM from 'react-dom';
import Batch from './middle';

// This method is only called once
// {/* <Post url="/api/v1/posts/1/" />, */}

window.onbeforeunload = function () {
  console.log("jumping to top");
  window.scrollTo(0, 0);
}

ReactDOM.render(
  // Insert the post component into the DOM
  <Batch url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
