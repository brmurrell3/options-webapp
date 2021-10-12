import React from 'react';
import PropTypes, { string } from 'prop-types';
import moment from 'moment';


// might need to make a put resquest here as the data gets updated
function trigger_like(data) {
  if (data.self_like) {
    data.likes = data.likes - 1;
    data.self_like = false;
  }
  else {
    data.likes = data.likes + 1;
    data.self_like = true;
  }
}

// determines what gets printed in the like/ unlike button
function like_vs_unlike(self_like_in) {
  if (self_like_in) {
    return 'unlike';
  }
  else {
    return 'like';
  }
}

// prints like vs likes depending on ct
function sing_like_vs_plur_likes(likes_in) {
  if (likes_in === 1) {
    return likes_in + ' like';
  }
  else {
    return likes_in + ' likes';
  }
}

// decides wether to have a delete button
function serve_delete_button(lognameOwnsThis) {
  if (lognameOwnsThis) {
    return (
      <button className="delete-comment-button" onClick={handleDeleteComment}>
        delete
      </button>
    );
  }
}

// deletes the comment
function handleDeleteComment(data) {
  data.handleDeleteComment;
}

// displays the comments
function display_comments(comments) {
  const listItems = comments.map((d) => 
  <div>
    <a href={d.ownerShowUrl} className="each-comment" key={d.text}>
      <strong>{d.owner}</strong> {d.text}
    </a>
    {serve_delete_button(d.lognameOwnsThis)}
  </div>);

  return (<div>{listItems}</div>);
}

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { imgUrl: '', 
    owner: '', timeStamp: '', 
    ownerUrl: '', ownerImgUrl: '', 
    postShowUrl: '', likes: '', 
    lognameLikesThis: true, postid: '', 
    comments: [], likeid: '', inputText: ''}

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  

  componentDidMount() {

    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {

        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          timeStamp: moment(data.created).fromNow(),
          ownerUrl: data.ownerShowUrl,
          ownerImgUrl: data.ownerImgUrl,
          postShowUrl: data.postShowUrl,
          likes: data.likes.numLikes,
          lognameLikesThis: data.likes.lognameLikesThis,
          postid: data.postid, comments: [...data.comments], 
          likeid: data.likes.url
        });
      })
      .catch((error) => console.log(error));
  }


  // handles the click of the like button
  handleLike = () => {
    if (this.state.lognameLikesThis) {
      let deleter = this.state.likeid;
      fetch(deleter, {credentials: 'same-origin', method: 'DELETE'}) 
      .then((response) => {
        if (!response.ok) throw Error (response.statusText);
        // return response.json();
      })
      .catch((error) => console.log(error));
      this.setState ({
        likes: this.state.likes - 1,
        lognameLikesThis: false
      });
    }
    else {
      let add_like_url = 'api/v1/likes/?postid=' + this.state.postid
      fetch(add_like_url, {credentials: 'same-origin', method: 'POST'}) // POST REQUEST
      .then((response) => {
        if (!response.ok) throw Error (response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState ({
          likes: this.state.likes + 1,
          lognameLikesThis: true,
          likeid: '/api/v1/likes/' + data.likeid + '/'
        });
      })
      .catch((error) => console.log(error));
    }
  }

  // allows the double clicking of an image
  // OPtional add a like animation
  handleDoubleClick = () => {
    if (this.state.lognameLikesThis) {}
    else {
      let add_like_url = 'api/v1/likes/?postid=' + this.state.postid
      fetch(add_like_url, {credentials: 'same-origin', method: 'POST'}) // POST REQUEST
        .then((response) => {
          if (!response.ok) throw Error (response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState ({
            likes: this.state.likes + 1,
            lognameLikesThis: true,
            likeid: '/api/v1/likes/' + data.likeid + '/'
          });
          // console.log("via delte url---" this.state.likeid);
        })
        .catch((error) => console.log(error));
    }
  }
//////////////////////////////////////COMMENTS FUNCTIONS///////////////////////////////////////////
  handleChange(event) {    
    this.setState({inputText: event.target.value});  
  }

  handleSubmit(event) {
    event.preventDefault();
    let comments_url = 'api/v1/comments/?postid=' + this.state.postid;
    fetch(comments_url, {
      'Content-Type': 'application/json',
      credentials: 'same-origin', 
      method: 'POST',
      body: JSON.stringify({
        text: this.state.inputText})
    }) // POST REQUEST
      .then((response) => {
        if (!response.ok) throw Error (response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState ({
          comments: this.state.comments.concat({
            'text': this.state.inputText, 
            'owner': data.owner, 
            'ownerShowUrl': data.ownerShowUrl,
            'lognameOwnsThis': data.lognameOwnsThis,
            'commentid': data.commentid,
            'url': data.url
          }), inputText: ''
        });
        // console.log("via delte url---" this.state.likeid);
        console.log(data);
      })
      .catch((error) => console.log(error));
  }

  handleDeleteComment = () => {
    let deleter = this.state.likeid;
      fetch(deleter, {credentials: 'same-origin', method: 'DELETE'}) 
      .then((response) => {
        if (!response.ok) throw Error (response.statusText);
        // return response.json();
      })
      .catch((error) => console.log(error));
      this.setState ({
        likes: this.state.likes - 1,
        lognameLikesThis: false
      });
  }



  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, timeStamp, ownerUrl, ownerImgUrl, postShowUrl, likes, lognameLikesThis, comments, postid, inputText} = this.state;

    // Render number of post image and post owner
    return (
      <div className="post">
        <div className="wrapper">
            <div className="container">
                <a href={ownerUrl}>
                    <img className="pfp" src={ownerImgUrl} alt="profile-picture"/>
                </a>
                <div className="account">
                    <a href={ownerUrl} className="username">
                        <p><strong>{owner}</strong></p>
                    </a>
                    <a href={postShowUrl} className="time">
                        <p>{timeStamp}</p>
                    </a>
                </div>
            </div>
            <div className="picture" onDoubleClick={this.handleDoubleClick}>
                <img src={imgUrl} alt="image"/>
            </div>
            <div className="container-bottom">
              {/* like and unlike button */}
              <div className="like">
                <button className="like-unlike-button" onClick={this.handleLike} type="button">
                  {like_vs_unlike(lognameLikesThis)}
                </button>
                {/* number of likes */}
                <div className="likes">
                  {sing_like_vs_plur_likes(likes)}
                </div>
              </div>
              {/* generated comments */}
              <div className="comments">
                {display_comments(comments)}
              </div>
              {/* replies */}
              <div className="reply">
                <form className="comment-form" onSubmit={this.handleSubmit}>
                  <input className="comment" type="text" placeholder="Add a comment..." value={inputText} onChange={this.handleChange}/>
                </form>
              </div>
            </div>
        </div>
      </div>  
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;