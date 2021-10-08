import React from 'react';
import ReactDOM from 'react-dom';
import Post from './post';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Post url="/api/v1/posts/1/" />,
  entry = document.getElementById('reactEntry'),
);



function handleResponse (response) {
  return response.json();
}



function display_posts(entry) {


  fetch("/api/v1/posts/1/")
  .then(handleResponse)

  const posts = []

  posts.forEach((post) => {
    const n = document.createElement('p');
    const s = `${user.username} has ${user.snippets.length} snippets`;
    const t = document.createTextNode(s);
    n.appendChild(t);
    entry.appendChild(n);
    });
}