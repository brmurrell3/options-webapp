import React from "react";
import PropTypes, { string } from "prop-types";
// import moment from "moment";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";




class Batch extends React.Component {
  constructor(props) {
    super(props);
    this.state = { links: [], next:''};
  }

  fetchData = () => {
    console.log(this.state.next);
    fetch(this.state.next, { credentials: "same-origin", method: "GET" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data.results);
        this.setState({
          links: this.state.links.concat(data.results),
          next: data.next
        });
      })
      .catch((error) => console.log(error));
  }



  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: "same-origin", method: "GET" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data);
        this.setState({
          links: data.results,
          next: data.next
        });
      })
      .catch((error) => console.log(error));
  }

  dummy() {
    

  }

  render() {
    const { links, next } = this.state;
    return (
      <InfiniteScroll
      dataLength={links.length}
      next={this.fetchData}
      hasMore={true}
      loader={<h4 style={{ textAlign: 'center', color: "lightslategray" }}>Loading...</h4>}
      endMessage={
        <p style={{ textAlign: 'center' }}>
          <b>Yay! You have seen it all</b>
        </p>
      }  
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
