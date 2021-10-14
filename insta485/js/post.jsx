import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

// determines the text on the like button
function LikeVsUnlike(selfLikeIn) {
  if (selfLikeIn) {
    return 'unlike';
  }
  return 'like';
}

// removes vals from arrIn
function shrinkArray(arrIn, commentIdIn) {
  for (let i = arrIn.length - 1; i >= 0; i -= 1) {
    if (arrIn[i].commentid === commentIdIn) {
      arrIn.splice(i, 1);
    }
  }
}

// determines wordage attached to num likes
function singLikeVsPlurLike(likesIn) {
  if (likesIn === 1) {
    return `${likesIn} like`;
  }
  return `${likesIn} likes`;
}

class Post extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      timeStamp: '',
      ownerUrl: '',
      ownerImgUrl: '',
      postShowUrl: '',
      likes: '',
      lognameLikesThis: true,
      postid: '',
      comments: [],
      likeid: '',
      inputText: '',
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleLike = this.handleLike.bind(this);
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
    this.createComment = this.createComment.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
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
          timeStamp: moment.utc(data.created).fromNow(),
          ownerUrl: data.ownerShowUrl,
          ownerImgUrl: data.ownerImgUrl,
          postShowUrl: data.postShowUrl,
          likes: data.likes.numLikes,
          lognameLikesThis: data.likes.lognameLikesThis,
          postid: data.postid,
          comments: [...data.comments],
          likeid: data.likes.url,
        });
      })
      .catch((error) => console.log(error));
  }

  // handles the click of the like button
  handleLike() {
    const {
      likeid,
      likes,
      postid,
      lognameLikesThis,
    } = this.state;
    if (lognameLikesThis) {
      const deleter = likeid;
      fetch(deleter, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          // return response.json();
        })
        .catch((error) => console.log(error));
      this.setState({
        likes: likes - 1,
        lognameLikesThis: false,
      });
    } else {
      const addLikeUrl = `api/v1/likes/?postid=${postid}`;
      fetch(addLikeUrl, { credentials: 'same-origin', method: 'POST' }) // POST REQUEST
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            likes: likes + 1,
            lognameLikesThis: true,
            likeid: `/api/v1/likes/${data.likeid}/`,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  // allows the double clicking of an image
  // OPtional add a like animation
  handleDoubleClick() {
    const { lognameLikesThis, postid, likes } = this.state;
    if (lognameLikesThis === false) {
      const addLikeUrl = `api/v1/likes/?postid=${postid}`;
      fetch(addLikeUrl, { credentials: 'same-origin', method: 'POST' }) // POST REQUEST
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            likes: likes + 1,
            lognameLikesThis: true,
            likeid: `/api/v1/likes/${data.likeid}/`,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  handleChange(event) {
    this.setState({ inputText: event.target.value });
  }

  // displays the comments
  displayComment(comments) {
    const listItems = comments.map((d) => (
      <div key={d.commentid} className="each-comment">
        <a href={d.ownerShowUrl} key={d.commentid}>
          <strong>{d.owner}</strong>
          {` ${d.text}`}
        </a>
        {this.serveDeleteButton(d.lognameOwnsThis, d.commentid)}
      </div>
    ));
    return (<div>{listItems}</div>);
  }

  // decides wether to have a delete button
  serveDeleteButton(lognameOwnsThis, commentid) {
    if (lognameOwnsThis) {
      return (
        <button
          className="delete-comment-button"
          onClick={() => this.deleteComment(commentid)}
          type="button"
        >
          delete
        </button>
      );
    }
    return (null);
  }

  createComment(event) {
    const { postid, comments, inputText } = this.state;
    event.preventDefault();
    const commentsUrl = `api/v1/comments/?postid=${postid}`;
    fetch(commentsUrl, {
      'Content-Type': 'application/json',
      credentials: 'same-origin',
      method: 'POST',
      body: JSON.stringify({
        text: inputText,
      }),
    }) // POST REQUEST
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: comments.concat({
            text: inputText,
            owner: data.owner,
            ownerShowUrl: data.ownerShowUrl,
            lognameOwnsThis: data.lognameOwnsThis,
            commentid: data.commentid,
            url: data.url,
          }),
          inputText: '',
        });
        // console.log('via delte url---' this.state.likeid);
        console.log(data);
      })
      .catch((error) => console.log(error));
  }

  // deletes a comment
  deleteComment(commentIdIn) {
    const { comments } = this.state;
    const deleter = `/api/v1/comments/${commentIdIn}/`;
    fetch(deleter, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .catch((error) => console.log(error));
    shrinkArray(comments, commentIdIn);
    const temp = comments;
    this.setState({
      comments: temp,
    });
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl,
      owner,
      timeStamp,
      ownerUrl,
      ownerImgUrl,
      postShowUrl,
      likes,
      lognameLikesThis,
      comments,
      postid,
      inputText,
    } = this.state;

    // Render number of post image and post owner
    return (
      <div key={postid} className="post">
        <div className="wrapper">
          <div className="container">
            <a href={ownerUrl}>
              <img className="pfp" src={ownerImgUrl} alt="profile" />
            </a>
            <div className="account">
              <a href={ownerUrl} className="username">
                <p>
                  <strong>{owner}</strong>
                </p>
              </a>
              <a href={postShowUrl} className="time">
                <p>{timeStamp}</p>
              </a>
            </div>
          </div>
          <div className="picture" onDoubleClick={this.handleDoubleClick}>
            <img src={imgUrl} alt="post-body" />
          </div>
          <div className="container-bottom">
            {/* like and unlike button */}
            <div className="like">
              <button
                className="like-unlike-button"
                onClick={this.handleLike}
                type="button"
              >
                {LikeVsUnlike(lognameLikesThis)}
              </button>
              {/* number of likes */}
              <div className="likes">{singLikeVsPlurLike(likes)}</div>
            </div>
            {/* generated comments */}
            <div className="comments">{this.displayComment(comments)}</div>
            {/* replies */}
            <div className="reply">
              <form className="comment-form" onSubmit={this.createComment}>
                <input
                  className="comment"
                  type="text"
                  placeholder="Add a comment..."
                  value={inputText}
                  onChange={this.handleChange}
                />
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
