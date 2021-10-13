import React from 'react';
import ReactDOM from 'react-dom';
import Post from './post';

// generate the 10 newest posts
function init_index() {

  const posts = []
  // Call REST API to get the post's information
  fetch('/api/v1/posts/', { credentials: 'same-origin', method: 'GET'})
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then((data) => {
      console.log(data.results);
      console.log("hello");

      // array1.forEach(element => console.log(element));

      (data.results).forEach((post) => {
        console.log("xxxxx" + post.url);
        let temp = <Post url={post.url}/>
        posts.push(temp);

      })

      console.log(posts);
      console.log(<Post url="/api/v1/posts/1/" />);

      return posts;
      
    })
    .catch((error) => console.log(error));
}


// This method is only called once
// {/* <Post url="/api/v1/posts/1/" />, */}
ReactDOM.render(
  // Insert the post component into the DOM


  <NumberList numbers={numbers} />,
  document.getElementById('reactEntry'),
);

// function showPosts() {

//   const entry = document.getElementById('reactEntry');

//   function handleResponse (response) {
//     if (!response.ok) throw Error(response.statusText);
//     return response.json();
//   }

//   function handleError(error) {
//       console.log(error);
//   }

//   function handleData(data) {


//     const posts = data.results;
//     posts.forEach((post) => {
    
//       // create item.owner href `${post.ownerShowUrl}`
//       const profileName = document.createElement('a');
//       profileName.href = 'post.ownerShowUrl';
      
//       // post header pfp
//       const ownerImgUrl = document.createElement('img');
//       // ownerImgUrl.className = 'pfp';
//       ownerImgUrl.src = 'post.ownerImgUrl';
//       ownerImgUrl.alt = 'post.ownerImgUrl-post';
//       profileName.appendChild(ownerImgUrl); // apprending the first part here
//       entry.appendChild(profileName);

//       // post header username
//       const ownerUsername = document.createElement('a');
//       ownerUsername.href = 'post.ownerShowUrl';
//       ownerUsernameText = document.createTextNode('post.ownerShowUrl');
//       ownerUsername.appendChild(ownerUsernameText);
//       entry.appendChild(ownerUsername);
      

//       // post header time
//       const postTimestamp = document.createElement('a');
//       postTimestamp.href = 'post.postShowUrl';
//       postTimestampText = document.createTextNode(moment('post.created', 'YYYY-MM-DD hh:mm:ss'));
//       postTimestamp.appendChild(postTimestampText);
//       entry.appendChild(postTimestamp);

//       // post picture 
//       const postPicture = document.createElement('img');
//       postPicture.src = 'post.imgUrl';
//       ownerImgUrl.alt = 'post.ownerImgUrl-post';
//       entry.appendChild(postPicture);

//       // remaining stuff is like and comment boxes.
//     });
//   }


//   fetch("/api/v1/posts/1/")
//     .then(handleResponse)
//     .then(handleData)
//     .catch(handleError);
// }

