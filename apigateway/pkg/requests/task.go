package requests

type TaskRequest struct {
	Username    string            `json:"username"`
	TaskName    string            `json:"taskName"`
	Title       string            `json:"title"`
	Description string            `json:"description"`
	Tokens      []string          `json:"tokens"`
	Meta        map[string]string `json:"meta"`
}
