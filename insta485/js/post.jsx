import React from 'react';
import PropTypes from 'prop-types';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { imgUrl: '', owner: '', timeStamp: '', ownerUrl: '', ownerImgUrl: '', postShowUrl: ''};
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
          postShowUrl: data.postShowUrl
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, timeStamp, ownerUrl, ownerImgUrl, postShowUrl} = this.state;

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
              <form className="comment-form">
                <input type="text" value=""/>
              </form>
              <button className="like-unlike-button">
                like
              </button>

              <button className="delete-comment-button">
                delete
              </button>
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