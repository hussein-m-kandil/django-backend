const serverErrorHTMLMessage = () => {
  return `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <strong>Sorry</strong>, <em>we cannot proceed your request right now!</em><br>
            <strong>Please try again later.</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
            </button>
        </div>
    `;
};

let rootURLElement = document.getElementById("root-url");
const ROOT_URL = rootURLElement.innerText;
rootURLElement.remove();
const createNewComment = (commentObject, postID) => {
  return `
    <div class="comment-on-post-${postID} m-3 border round p-2 shadow-sm">
      <div class="d-flex justify-content-between align-items-center">
        <div class="me-2" style="max-height: 7.5%; max-width: 7.5%;">
          <img class="w-100 rounded border border-dark opacity-75"
            src="/static/monotext/images/${
              commentObject.ownerPic === 0 ? "woman.jpg" : "man.jpg"
            }"
            alt="The profile picture of post's owner.">
        </div>
        <div class="w-100 d-flex justify-content-between align-items-center">
          <div class="h6 text-start m-0">
            <a href="${
              ROOT_URL + "profile/" + commentObject.ownerName
            }" class="d-block text-decoration-none link-secondary">
              <strong><em>${commentObject.ownerName}</em></strong>
            </a>
          </div>
          <div class="d-block h6 text-secondary text-end m-0">
            <em>${commentObject.createdAt}</em>
          </div>
        </div>
      </div>
      <hr class="mt-1 text-secondary">
      <div class="h6 text-center" style="min-height: 3em;">
        ${commentObject.text}
      </div>
    </div>
  `;
};

const getPostCommentsChunk = async (url) => {
  try {
    const response = await fetch(url, {
      method: "GET",
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      console.log("Response =>\n", response);
      return false;
    }
  } catch (error) {
    console.log("Error =>\n", error);
    return false;
  }
};

const postCommentsPopulation = async (postID, commentsLink) => {
  await commentsLink.addEventListener("click", (event) => {
    event.preventDefault();
    const lessCommentsLinkText = "... Less comments";
    const postMoreCommentsLink = event.target;
    const postCommentsDiv = document.getElementById("post-comments-" + postID);
    const commentsPageCounter = document.getElementById(
      "comments-page-counter-" + postID
    );
    const postCommentsURL = document.getElementById(
      "post-comments-url-" + postID
    ).innerText;
    const url = postCommentsURL + "?page=" + commentsPageCounter.innerText;
    getPostCommentsChunk(url).then((data) => {
      if (data.commentsCount > 0) {
        if (postMoreCommentsLink.innerText == lessCommentsLinkText) {
          postCommentsDiv.innerHTML = "";
          postMoreCommentsLink.innerText = "More comments...";
          postCommentsDiv.appendChild(postMoreCommentsLink);
        }
        postCommentsDiv.removeChild(postMoreCommentsLink);
        for (let i = 0; i < data.commentsChunk.length; i++) {
          postCommentsDiv.innerHTML += createNewComment(
            data.commentsChunk[i],
            postID
          );
        }
        postCommentsDiv.appendChild(postMoreCommentsLink);
        if (data.hasNext) {
          commentsPageCounter.innerText =
            Number(commentsPageCounter.innerText) + 1;
          postMoreCommentsLink.style.display = "block";
        } else {
          commentsPageCounter.innerText = 1;
          if (data.commentsCount > 2) {
            postMoreCommentsLink.innerText = lessCommentsLinkText;
          } else {
            postMoreCommentsLink.style.display = "none";
          }
        }
      }
    });
  });
};

const formHandler = async (
  url,
  form,
  errorsDiv,
  textField,
  titleField = false
) => {
  const formData = new FormData(form);
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (response.redirected) {
      if (titleField) {
        // It was a new post submission
        window.location.href = response.url;
      } else {
        // Although, it was a new comment submission,
        // i won't update the comments with the new comment interactively :D
        window.location.href = response.url;
      }
      form.elements.text.value = "";
    } else if (response.ok) {
      const data = await response.json();
      if (data.text && data.text.length > 0) {
        textField.classList.add("is-invalid");
        for (let i = 0; i < data.text.length; i++) {
          errorsDiv.innerHTML += `
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            ${data.text[i]}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
                            </button>
                        </div>
                    `;
        }
      }
    } else {
      console.log("Response =>\n", response);
      errorsDiv.innerHTML += serverErrorHTMLMessage();
      return false;
    }
    return true;
  } catch (e) {
    console.log("Error =>\n", e);
    errorsDiv.innerHTML += serverErrorHTMLMessage();
    return false;
  }
};

const likesRequestsHandler = async (
  url,
  csrfTokenValue,
  likesCounterElement,
  buttonToHide,
  buttonToShow
) => {
  let formData = new FormData();
  formData.append("csrfmiddlewaretoken", csrfTokenValue);
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (response.redirected && response.url.includes("?next=")) {
      window.location.href = response.url;
      return true;
    } else if (response.ok) {
      try {
        const jsonResponse = await response.json();
        likesCounterElement.innerText = jsonResponse.likes;
        buttonToHide.style.display = "none";
        buttonToShow.style.display = "block";
        return true;
      } catch (error) {
        console.log("Error =>\n", error);
        return false;
      }
    } else {
      console.log("Response =>\n", response);
      return false;
    }
  } catch (error) {
    console.log("Error =>\n", error);
    return false;
  }
};

let postForm = document.getElementById("post-form");
postForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.target;
  const url = form.action;
  const errorsDiv = form.children.errorsDiv;
  const textField = form.elements.text;
  textField.addEventListener("input", (event) => {
    event.target.classList.remove("is-invalid");
  });
  const titleField = form.elements.title;
  titleField.addEventListener("input", (event) => {
    event.target.classList.remove("is-invalid");
  });
  formHandler(url, form, errorsDiv, textField, titleField);
});
// Create post form display logic
document
  .getElementById("post-form-display-button")
  ?.addEventListener("click", (event) => {
    event.preventDefault();
    if (postForm?.classList[0] == "d-none") {
      postForm.classList.remove("d-none");
      postForm.classList.add("d-flex", "flex-column");
    } else if (postForm?.classList[0] == "d-flex") {
      postForm.classList.remove("d-flex", "flex-column");
      postForm.classList.add("d-none");
    }
  });

const postCommentsDiv = document.getElementsByClassName("post-comments-div");
for (let i = 0; i < postCommentsDiv?.length; i++) {
  const postID = postCommentsDiv[i].id.match(/\d+/)[0];
  const postMoreCommentsLink = document.getElementById(
    "post-more-comments-link-" + postID
  );
  postCommentsPopulation(postID, postMoreCommentsLink).then((_) => {
    postMoreCommentsLink.click();
  });
}

const commentFormsList = document.getElementsByClassName("comment-form");
for (let i = 0; i < commentFormsList?.length; i++) {
  commentFormsList[i].addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.target;
    const url = form.action;
    const textField = form.elements.text;
    textField.addEventListener("input", (event) => {
      event.target.classList.remove("is-invalid");
    });
    const errorsDiv = form.children.errorsDiv;
    formHandler(url, form, errorsDiv, textField);
  });
}

// Post likes logic
const CSRFTokenInput = document.getElementsByName("csrfmiddlewaretoken")[0];
if (CSRFTokenInput) {
  const postLikesCountList =
    document.getElementsByClassName("post-likes-count");
  for (let i = 0; i < postLikesCountList?.length; i++) {
    const postID = postLikesCountList[i]?.id.match(/\d+/)[0];
    const postLikesCountSpan = document.getElementById(
      "post-likes-count-number-" + postID
    );
    // Like list logic
    let likesModalElement = document.getElementById("likes-modal-" + postID);
    let likesModal;
    if (likesModalElement) {
      likesModal = new bootstrap.Modal(likesModalElement);
    }
    let likesModalDialog = document.getElementById(
      "likes-modal-dialog-" + postID
    );
    if (likesModal && likesModalDialog) {
      let moreLikersLink = likesModalDialog.lastElementChild;
      moreLikersLink.addEventListener("click", (event) => {
        event.preventDefault();
        postLikesCountSpan?.parentElement?.click();
      });
      let likeListPageCounter = 0;
      let fulfilled = false;
      postLikesCountSpan?.parentElement?.addEventListener("click", (event) => {
        event.preventDefault();
        likesModal.show();
        likeListPageCounter += !fulfilled ? 1 : 0;
        // Get like list
        let likesURL = event.target.href;
        try {
          fetch(likesURL + "?page=" + likeListPageCounter.toString()).then(
            (response) => {
              if (response.ok) {
                try {
                  response.json().then((data) => {
                    // Fill the modal with the list
                    const likes = data.likes;
                    if (likesModalDialog.contains(moreLikersLink)) {
                      likesModalDialog.removeChild(moreLikersLink);
                    }
                    if (data.totalLikes < 1) {
                      fulfilled = true;
                      likesModalDialog.innerHTML = `
                        <p class="text-center">
                          There are no likes on this post.
                        </p>
                      `;
                    }
                    if (!fulfilled) {
                      for (let i = 0; i < likes.length; i++) {
                        likesModalDialog.innerHTML += `
                        <div class="d-flex justify-content-around align-items-center my-3">
                          <div class="m-auto">
                              <a id="liker-name-${postID}" 
                                href="${likes[i].ownerProfilePage}" 
                                class="link-dark text-decoration-none h4 text-left">
                                <strong>${likes[i].ownerName}</strong>
                              </a>
                              <br>
                              <span id="like-date-${postID}" class="h6 text-left text-muted">
                                ${likes[i].createdAt}
                              </span>
                          </div>
                          <div class="m-auto" style="width: 15%;">
                            <img id="liker-img-${postID}" 
                              class="d-block w-100 m-auto me-0 rounded border border-dark"
                                src="/static/monotext/images/${
                                  likes[i].ownerPic == 0
                                    ? "woman.jpg"
                                    : "man.jpg"
                                }"
                                alt="The profile picture of like's owner.">
                          </div>
                        </div>
                      `;
                      }
                    }
                    // Control the presence of 'more likers' link and avoid redundancy the list fulfilled
                    if (
                      data.totalLikes > likeListPageCounter * data.chunkSize &&
                      !fulfilled
                    ) {
                      moreLikersLink.style.display = "block";
                      likesModalDialog.appendChild(moreLikersLink);
                    } else {
                      likeListPageCounter = 0;
                      fulfilled = true;
                      moreLikersLink.style.display = "none";
                    }
                  });
                } catch (error) {
                  likesModalDialog.innerHTML = `
                    <p class="text-center text-danger">
                      Can't fetch any data! try again later.
                    </p>
                  `;
                  likesModalDialog.appendChild(moreLikersLink);
                  console.log("Like List JSON Error =>\n", error);
                }
              } else {
                likesModalDialog.innerHTML = `
                  <p class="text-center text-danger">
                    Can't fetch any data! try again later.
                  </p>
                `;
                likesModalDialog.appendChild(moreLikersLink);
                console.log("Like List Response Not Ok =>\n", response);
              }
            }
          );
        } catch (error) {
          likesModalDialog.innerHTML = `
            <p class="text-center text-danger">
              Can't fetch any data! try again later.
            </p>
          `;
          likesModalDialog.appendChild(moreLikersLink);
          console.log("Fetch Error =>\n", error);
        }
      });
    }
    // Like/Dislike logic
    const likeButton = document.getElementById("like-btn-" + postID);
    const dislikeButton = document.getElementById("dislike-btn-" + postID);
    likeButton?.addEventListener("click", (event) => {
      event.preventDefault();
      likesRequestsHandler(
        likeButton.value,
        CSRFTokenInput.value,
        postLikesCountSpan,
        likeButton,
        dislikeButton
      ).then((isOk) => {
        return isOk;
      });
    });
    dislikeButton?.addEventListener("click", (event) => {
      event.preventDefault();
      likesRequestsHandler(
        dislikeButton.value,
        CSRFTokenInput.value,
        postLikesCountSpan,
        dislikeButton,
        likeButton
      ).then((isOk) => {
        return isOk;
      });
    });
  }
}
