import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Batch extends React.Component {
  constructor(props) {
    super(props);
    this.state = { links: [], next: '' };
  }

  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data);
        this.setState({
          links: data.results,
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchData() {
    const { next, links } = this.state;
    fetch(next, { credentials: 'same-origin', method: 'GET' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data.results);
        this.setState({
          links: links.concat(data.results),
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { links } = this.state;
    return (
      <InfiniteScroll
        dataLength={links.length}
        next={this.fetchData}
        hasMore={true}
        loader={<h4 style={{ textAlign: 'center', color: 'lightslategray' }}>Loading...</h4>}
        endMessage={(
          <p style={({ textAlign: 'center' })}>
            <b>Yay! You have seen it all</b>
          </p>
        )}
      >
        <section className="feed">
          {links.map((post) => (
            <div className="">
              <Post url={post.url} />
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
