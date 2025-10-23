# TODO: Fix Admin Personnel Page Photo Preview and Modal Handling

## Steps to Complete:
- [x] Add photo preview `<img>` element in the modal's photo form-group.
- [x] Update `openAddModal` function to set the preview to the default image.
- [x] Update `openEditModal` function to accept an image URL parameter and set the preview accordingly.
- [x] Update the edit button's onclick attribute in the table to pass the counselor's image URL to `openEditModal`.
- [x] Add an event listener for the file input (`counselorPhoto`) to update the photo preview when a new file is selected.
- [x] Test the modal for add/edit modes, ensure photo preview works, form submits correctly, and page reloads after success.
