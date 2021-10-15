import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Batch extends React.Component {
  constructor(props) {
    super(props);
    this.state = { links: [], next: '' };
    this.fetchData = this.fetchData.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          links: data.results,
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchData() {
    const { next } = this.state;
    fetch(next, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          links: prevState.links.concat(data.results),
          next: data.next,
        }));
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { links, next } = this.state;
    return (
      <InfiniteScroll
        dataLength={links.length}
        next={this.fetchData}
        hasMore={next}
        loader={<h4 style={{ textAlign: 'center', color: 'lightslategray' }}>Loading...</h4>}
        endMessage={(
          <p style={({ textAlign: 'center' })}>
            <b>Yay! You have seen it all</b>
          </p>
        )}
      >
        <section className="feed">
          {links.map((post) => (
            <div key={post.postid}>
              <Post data={JSON.stringify(post)} />
            </div>
          ))}
        </section>
      </InfiniteScroll>
    );
  }
}

Batch.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Batch;
