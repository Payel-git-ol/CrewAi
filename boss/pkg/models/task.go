package models

type Task struct {
	Username    string
	TaskName    string
	Title       string
	Description string
	Tokens      []string
	Meta        map[string]string
}
