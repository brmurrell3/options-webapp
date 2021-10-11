import React from 'react';
import PropTypes from 'prop-types';


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
  console.log("entered");
  console.log(data);


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
    lognameLikesThis: true};
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
          timeStamp: data.created,
          ownerUrl: data.ownerShowUrl,
          ownerImgUrl: data.ownerImgUrl,
          postShowUrl: data.postShowUrl,
          likes: data.likes.numLikes,
          lognameLikesThis: data.likes.lognameLikesThis,
        });
      })
      .catch((error) => console.log(error));
      console.log(this.state);

  }

  // handles the click of the like button
  handleLike = () => {
    console.log("endter :)");

    this.setState ({
    });
    console.log(this.state);

    if (this.state.lognameLikesThis) {
      this.setState ({
        likes: this.state.likes - 1,
        lognameLikesThis: false
      });
    }
    else {
      this.setState ({
        likes: this.state.likes + 1,
        lognameLikesThis: true
      });
    }
    // console.log("entered");
    // console.log(data);
  
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, timeStamp, ownerUrl, ownerImgUrl, postShowUrl, likes, lognameLikesThis} = this.state;

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
            <div className="picture">
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

              </div>
              {/* replies */}
              <div className="reply">
                <form className="comment-form">
                  <input className="comment" type="text" placeholder="type here" value=""/>
                </form>
                <button className="delete-comment-button">
                delete
                </button>
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